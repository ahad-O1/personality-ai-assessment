import os
import sys
import django
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "personality_ai.settings")
django.setup()
from recommendations.models import Career


MODEL_PATH = "ml/models/career_model.pkl"


def rule_score(user_scores, career):
    scores = []

    trait_checks = [
        ("openness", career.min_openness, "min"),
        ("conscientiousness", career.min_conscientiousness, "min"),
        ("extraversion", career.min_extraversion, "min"),
        ("agreeableness", career.min_agreeableness, "min"),
        ("neuroticism", career.max_neuroticism, "max"),
    ]

    for trait, target, rule_type in trait_checks:
        user_value = user_scores[trait]

        if rule_type == "min":
            score = min((user_value / target) * 100, 100) if target > 0 else 100
        else:
            score = min((target / user_value) * 100, 100) if user_value > 0 else 100

        scores.append(score)

    return round(sum(scores) / len(scores), 2)


def ml_scores(user_scores):
    model = joblib.load(MODEL_PATH)

    input_data = pd.DataFrame([user_scores])
    probabilities = model.predict_proba(input_data)[0]
    classes = model.classes_

    return {
        career: round(prob * 100, 2)
        for career, prob in zip(classes, probabilities)
    }


def get_hybrid_recommendations(o, c, e, a, n, top_n=5):
    user_scores = {
        "openness": o,
        "conscientiousness": c,
        "extraversion": e,
        "agreeableness": a,
        "neuroticism": n,
    }

    ml_result = ml_scores(user_scores)

    final_results = []

    careers = Career.objects.filter(is_active=True)

    for career in careers:
        ml_score = ml_result.get(career.title, 0)
        rules_score = rule_score(user_scores, career)

        final_score = round((ml_score * 0.4) + (rules_score * 0.6), 2)

        final_results.append({
            "career": career.title,
            "category": career.category,
            "description": career.description,
            "skills": career.skills,
            "required_traits": career.required_traits,
            "ml_score": ml_score,
            "rule_score": rules_score,
            "final_score": final_score,
        })

    final_results = sorted(
        final_results,
        key=lambda x: x["final_score"],
        reverse=True
    )

    return final_results[:top_n]


if __name__ == "__main__":
    recommendations = get_hybrid_recommendations(
        o=80,
        c=85,
        e=40,
        a=55,
        n=25,
        top_n=5
    )

    print("Top Hybrid Career Recommendations:\n")

    for index, item in enumerate(recommendations, start=1):
        print(f"{index}. {item['career']} ({item['category']})")
        print(f"   Final Match: {item['final_score']}%")
        print(f"   ML Score: {item['ml_score']}%")
        print(f"   Rule Score: {item['rule_score']}%")
        print(f"   Skills: {item['skills']}")
        print()