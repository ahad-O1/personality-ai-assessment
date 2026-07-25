"""
Hybrid ML and rule-based career recommendation engine.
"""

from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings

from .ai_personality import get_match_label
from .ai_reason import generate_ai_reason, generate_ai_warning
from .models import Career
from .roadmap import generate_career_roadmap


MODEL_PATH = (
    Path(settings.BASE_DIR)
    / "ml"
    / "models"
    / "career_model.pkl"
)


def rule_score(user_scores, career):
    """Calculate rule-based compatibility between user and career."""

    scores = []

    traits = [
        ("openness", career.min_openness, "min"),
        (
            "conscientiousness",
            career.min_conscientiousness,
            "min",
        ),
        ("extraversion", career.min_extraversion, "min"),
        ("agreeableness", career.min_agreeableness, "min"),
        ("neuroticism", career.max_neuroticism, "max"),
    ]

    for trait, target, rule_type in traits:
        user_value = user_scores[trait]

        if rule_type == "min":
            score = (
                min((user_value / target) * 100, 100)
                if target > 0
                else 100
            )
        else:
            score = (
                min((target / user_value) * 100, 100)
                if user_value > 0
                else 100
            )

        scores.append(score)

    return round(sum(scores) / len(scores), 2)


def get_recommended_careers(result, top_n=5):
    """Return the highest-ranked hybrid career recommendations."""

    user_scores = {
        "openness": result.openness,
        "conscientiousness": result.conscientiousness,
        "extraversion": result.extraversion,
        "agreeableness": result.agreeableness,
        "neuroticism": result.neuroticism,
    }

    model = joblib.load(MODEL_PATH)

    input_data = pd.DataFrame([user_scores])
    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    ml_scores = {
        career_title: round(probability * 100, 2)
        for career_title, probability in zip(
            classes,
            probabilities,
        )
    }

    recommendations = []

    for career in Career.objects.filter(is_active=True):
        ml_score = ml_scores.get(career.title, 0)
        personality_score = rule_score(user_scores, career)

        final_score = round(
            (ml_score * 0.4)
            + (personality_score * 0.6),
            2,
        )

        recommendations.append({
            "id": career.id,
            "title": career.title,
            "category": career.category,
            "description": career.description,
            "required_traits": career.required_traits,
            "skills": career.skills,
            "ml_score": ml_score,
            "rule_score": personality_score,
            "final_score": final_score,
            "reasons": generate_ai_reason(result, career),
            "warnings": generate_ai_warning(result, career),
            "match_label": get_match_label(final_score),
            "roadmap": generate_career_roadmap(career),
        })

    return sorted(
        recommendations,
        key=lambda item: item["final_score"],
        reverse=True,
    )[:top_n]