"""
Career Recommendation Engine

Combines:
1. OCEAN rule-based compatibility
2. Career-level ML probability
3. ML career-category prediction
4. AI-generated reasons/warnings
5. Career roadmap
"""

from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings

from .ai_personality import get_match_label
from .ai_reason import generate_ai_reason, generate_ai_warning
from .models import Career
from .roadmap import generate_career_roadmap, generate_structured_roadmap

# Market metrics default lookup per category
MARKET_METRICS = {
    "Technology": {"salary": "$65,000 - $145,000", "growth": "+24% (Very High)", "stress": "Balanced / Moderate"},
    "Engineering": {"salary": "$70,000 - $135,000", "growth": "+19% (High Demand)", "stress": "Moderate"},
    "Business": {"salary": "$60,000 - $130,000", "growth": "+16% (Steady)", "stress": "Fast-Paced"},
    "Medical": {"salary": "$75,000 - $160,000", "growth": "+22% (Critical Demand)", "stress": "High Focus"},
    "Creative": {"salary": "$45,000 - $110,000", "growth": "+14% (Growing)", "stress": "Flexible"},
    "Education": {"salary": "$45,000 - $85,000", "growth": "+11% (Stable)", "stress": "Balanced"},
    "Public Service": {"salary": "$50,000 - $105,000", "growth": "+12% (Stable)", "stress": "Moderate"},
}


from ml.category_model.category_predictor import predict_category


# ============================================================
# PATHS
# ============================================================

CAREER_MODEL_PATH = (
    Path(str(getattr(settings, "BASE_DIR", ".")))
    / "ml"
    / "models"
    / "career_model.pkl"
)


# ============================================================
# CATEGORY MAPPING
# ============================================================

CATEGORY_MAPPING = {
    "Technology and IT": "Technology",
    "Engineering and Architecture": "Engineering",
    "Business Management and Finance": "Business",
    "Creative Media and Design": "Creative",
    "Education and Research": "Education",
    "Environmental Science": "Environmental",
    "Healthcare and Medical": "Medical",
    "Law Government and Security": "Public Service",
    "Social and Behavioral Sciences": "Social",
}


# ============================================================
# RELATED CATEGORIES
# ============================================================

RELATED_CATEGORIES = {
    "technology": {
        "engineering",
    },
    "engineering": {
        "technology",
    },
    "business": {
        "technology",
    },
    "education": {
        "social",
    },
    "social": {
        "education",
    },
    "medical": {
        "environmental",
    },
    "environmental": {
        "medical",
    },
}


# ============================================================
# PERSONALITY / RULE SCORE
# ============================================================

def rule_score(user_scores, career):
    """
    Calculate personality compatibility.

    Minimum requirements:
        O, C, E, A

    Maximum requirement:
        N
    """

    scores = []

    requirements = [
        (
            "openness",
            career.min_openness,
            "min",
        ),
        (
            "conscientiousness",
            career.min_conscientiousness,
            "min",
        ),
        (
            "extraversion",
            career.min_extraversion,
            "min",
        ),
        (
            "agreeableness",
            career.min_agreeableness,
            "min",
        ),
        (
            "neuroticism",
            career.max_neuroticism,
            "max",
        ),
    ]

    for trait, target, rule_type in requirements:

        user_value = float(
            user_scores.get(trait, 0) or 0
        )

        target = float(target or 0)

        # ----------------------------------------
        # Minimum requirement
        # ----------------------------------------

        if rule_type == "min":

            if target <= 0:
                score = 100.0
            else:
                score = (
                    user_value / target
                ) * 100

                score = min(
                    score,
                    100.0,
                )

        # ----------------------------------------
        # Maximum requirement
        # ----------------------------------------

        else:

            if target <= 0:

                # No maximum constraint
                score = 100.0

            elif user_value <= target:

                score = 100.0

            else:

                score = (
                    target / user_value
                ) * 100

                score = min(
                    score,
                    100.0,
                )

        scores.append(score)

    if not scores:
        return 0.0

    return round(
        sum(scores) / len(scores),
        2,
    )


# ============================================================
# CATEGORY PREDICTION
# ============================================================

def get_predicted_category(user_scores):
    """
    Predict career category from OCEAN scores.
    """

    try:

        prediction = predict_category(
            float(
                user_scores.get(
                    "openness",
                    0,
                )
                or 0
            ),
            float(
                user_scores.get(
                    "conscientiousness",
                    0,
                )
                or 0
            ),
            float(
                user_scores.get(
                    "extraversion",
                    0,
                )
                or 0
            ),
            float(
                user_scores.get(
                    "agreeableness",
                    0,
                )
                or 0
            ),
            float(
                user_scores.get(
                    "neuroticism",
                    0,
                )
                or 0
            ),
        )

    except Exception:

        return {
            "ml_category": None,
            "django_category": None,
            "confidence": 0.0,
            "hybrid_used": False,
            "engineering_probability": None,
            "technology_probability": None,
        }

    ml_category = prediction.get(
        "category"
    )

    try:
        confidence = float(
            prediction.get(
                "confidence",
                0,
            )
            or 0
        )

    except (
        TypeError,
        ValueError,
    ):

        confidence = 0.0

    django_category = (
        CATEGORY_MAPPING.get(ml_category)
        if ml_category
        else None
    )

    return {
        "ml_category": ml_category,
        "django_category": django_category,
        "confidence": round(
            confidence,
            6,
        ),
        "hybrid_used": prediction.get(
            "hybrid_used",
            False,
        ),
        "engineering_probability": prediction.get(
            "engineering_probability"
        ),
        "technology_probability": prediction.get(
            "technology_probability"
        ),
    }


# ============================================================
# CAREER ML SCORES
# ============================================================

_career_model = None


def get_ml_scores(user_scores):
    """
    Get Random Forest probability for every career.

    career_model.pkl was trained with exactly:

        openness
        conscientiousness
        extraversion
        agreeableness
        neuroticism
    """

    global _career_model

    try:

        if _career_model is None:
            if CAREER_MODEL_PATH.exists():
                _career_model = joblib.load(
                    CAREER_MODEL_PATH
                )

        if _career_model is None:
            return {}

        model = _career_model

        data = pd.DataFrame(
            [
                {
                    "openness": float(
                        user_scores["openness"]
                    ),
                    "conscientiousness": float(
                        user_scores[
                            "conscientiousness"
                        ]
                    ),
                    "extraversion": float(
                        user_scores[
                            "extraversion"
                        ]
                    ),
                    "agreeableness": float(
                        user_scores[
                            "agreeableness"
                        ]
                    ),
                    "neuroticism": float(
                        user_scores[
                            "neuroticism"
                        ]
                    ),
                }
            ]
        )

        probabilities = (
            model.predict_proba(data)[0]
        )

        classes = model.classes_

        return {
            str(career): round(
                float(probability) * 100,
                2,
            )
            for career, probability in zip(
                classes,
                probabilities,
            )
        }

    except Exception:

        return {}


# ============================================================
# CATEGORY SCORE
# ============================================================

def get_category_score(
    career_category,
    predicted_category,
    confidence,
):
    """
    Category compatibility.

    Same category:
        confidence * 100

    Related category:
        confidence * 50

    Different category:
        0

    This prevents a low-confidence category prediction
    from giving an artificial 100-point boost.
    """

    if not career_category:
        return 0.0

    if not predicted_category:
        return 0.0

    try:
        confidence = float(
            confidence or 0
        )

    except (
        TypeError,
        ValueError,
    ):

        confidence = 0.0

    confidence = max(
        0.0,
        min(
            confidence,
            1.0,
        ),
    )

    career_category = (
        str(career_category)
        .strip()
        .lower()
    )

    predicted_category = (
        str(predicted_category)
        .strip()
        .lower()
    )

    # ----------------------------------------
    # Exact category
    # ----------------------------------------

    if (
        career_category
        == predicted_category
    ):
        return round(
            confidence * 100,
            2,
        )

    # ----------------------------------------
    # Related category
    # ----------------------------------------

    related = RELATED_CATEGORIES.get(
        predicted_category,
        set(),
    )

    if career_category in related:

        return round(
            confidence * 50,
            2,
        )

    # ----------------------------------------
    # Different category
    # ----------------------------------------

    return 0.0


# ============================================================
# MAIN RECOMMENDATION ENGINE
# ============================================================

def get_recommended_careers(
    result,
    top_n=5,
):
    """
    Generate career recommendations.

    Final score:

        55% Rule-based personality score
        25% Career ML probability
        20% Category compatibility
    """

    if result is None:
        return []

    # ========================================================
    # USER OCEAN
    # ========================================================

    user_scores = {
        "openness": float(
            result.openness or 0
        ),
        "conscientiousness": float(
            result.conscientiousness or 0
        ),
        "extraversion": float(
            result.extraversion or 0
        ),
        "agreeableness": float(
            result.agreeableness or 0
        ),
        "neuroticism": float(
            result.neuroticism or 0
        ),
    }

    # ========================================================
    # CATEGORY MODEL
    # ========================================================

    category_result = (
        get_predicted_category(
            user_scores
        )
    )

    predicted_category = (
        category_result.get(
            "ml_category"
        )
    )

    predicted_django_category = (
        category_result.get(
            "django_category"
        )
    )

    category_confidence = float(
        category_result.get(
            "confidence",
            0,
        )
        or 0
    )

    # ========================================================
    # CAREER MODEL
    # ========================================================

    ml_scores = get_ml_scores(
        user_scores
    )

    # ========================================================
    # ACTIVE CAREERS
    # ========================================================

    careers = Career.objects.filter(
        is_active=True
    )

    recommendations = []

    # ========================================================
    # SCORE EACH CAREER
    # ========================================================

    for career in careers:

        # ----------------------------------------------------
        # 1. RULE SCORE
        # ----------------------------------------------------

        personality_score = rule_score(
            user_scores,
            career,
        )

        # ----------------------------------------------------
        # 2. CAREER ML SCORE
        # ----------------------------------------------------

        ml_score = float(
            ml_scores.get(
                career.title,
                0,
            )
            or 0
        )

        # ----------------------------------------------------
        # 3. CATEGORY SCORE
        # ----------------------------------------------------

        category_score = (
            get_category_score(
                career.category,
                predicted_django_category,
                category_confidence,
            )
        )

        # ----------------------------------------------------
        # 4. FINAL SCORE
        # ----------------------------------------------------

        final_score = (
            personality_score * 0.55
            + ml_score * 0.25
            + category_score * 0.20
        )

        final_score = round(
            max(
                0.0,
                min(
                    final_score,
                    100.0,
                ),
            ),
            2,
        )

        # ----------------------------------------------------
        # 5. CATEGORY MATCH
        # ----------------------------------------------------

        category_match = (
            predicted_django_category is not None
            and bool(career.category)
            and career.category.strip().lower()
            == predicted_django_category.strip().lower()
        )

        # ----------------------------------------------------
        # 6. CANDIDATE OBJECT
        # ----------------------------------------------------

        recommendations.append(
            {
                "_career_obj": career,
                "id": career.id,
                "title": career.title,
                "category": career.category,
                "description": career.description,
                "required_traits": career.required_traits,
                "skills": career.skills,

                "ml_score": round(
                    ml_score,
                    2,
                ),

                "rule_score": round(
                    personality_score,
                    2,
                ),

                "category_score": round(
                    category_score,
                    2,
                ),

                "category_match": (
                    category_match
                ),

                "predicted_category": (
                    predicted_category
                ),

                "predicted_category_mapped": (
                    predicted_django_category
                ),

                "category_confidence": round(
                    category_confidence,
                    6,
                ),

                "final_score": final_score,
            }
        )

    # ========================================================
    # SORT
    # ========================================================

    recommendations.sort(
        key=lambda item: (
            item["final_score"],
            item["rule_score"],
            item["ml_score"],
        ),
        reverse=True,
    )

    top_recs = recommendations[:top_n]

    # ========================================================
    # GENERATE AI DETAILS ONLY FOR TOP CAREERS
    # ========================================================

    for rec in top_recs:
        career = rec.pop("_career_obj")
        final_score = rec["final_score"]

        # AI Reasons
        try:
            reasons = generate_ai_reason(
                result,
                career,
            )
        except Exception:
            reasons = []

        # AI Warnings
        try:
            warnings = generate_ai_warning(
                result,
                career,
            )
        except Exception:
            warnings = []

        # Match Label
        try:
            match_label = get_match_label(
                final_score
            )
        except Exception:
            if final_score >= 75:
                match_label = "Strong Match"
            elif final_score >= 60:
                match_label = "Good Match"
            else:
                match_label = "Possible Match"

        # Roadmap & Structured Roadmap
        try:
            roadmap = generate_career_roadmap(career)
            structured_roadmap = generate_structured_roadmap(career)
        except Exception:
            roadmap = []
            structured_roadmap = []

        # Parse skills into list
        raw_skills = rec.get("skills", "")
        parsed_skills = [
            s.strip() for s in raw_skills.split(",") if s.strip()
        ]

        # Ideal OCEAN target benchmarks for career
        ideal_ocean = {
            "openness": max(50, career.min_openness),
            "conscientiousness": max(50, career.min_conscientiousness),
            "extraversion": max(40, career.min_extraversion),
            "agreeableness": max(40, career.min_agreeableness),
            "neuroticism": max(20, 100 - career.max_neuroticism),
        }

        # Market metrics
        metrics = MARKET_METRICS.get(
            career.category,
            {"salary": "$55,000 - $120,000", "growth": "+15% (Growing)", "stress": "Moderate"}
        )

        rec["reasons"] = reasons
        rec["warnings"] = warnings
        rec["match_label"] = match_label
        rec["roadmap"] = roadmap
        rec["structured_roadmap"] = structured_roadmap
        rec["parsed_skills"] = parsed_skills
        rec["ideal_ocean"] = ideal_ocean
        rec["salary_range"] = metrics["salary"]
        rec["market_growth"] = metrics["growth"]
        rec["stress_level"] = metrics["stress"]

    return top_recs