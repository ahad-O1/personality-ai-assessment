"""
Explainable AI helpers for career recommendations.
"""


def generate_ai_reason(result, career):
    """Generate reasons explaining why a career suits the user."""

    reasons = []
    title = career.title.lower()

    technology_keywords = [
        "software", "developer", "engineer", "data",
        "ai", "machine learning", "devops",
    ]

    creative_keywords = [
        "designer", "photographer", "artist",
        "video", "journalist", "writer",
    ]

    business_keywords = [
        "manager", "marketing", "sales", "hr",
    ]

    medical_keywords = [
        "doctor", "nutritionist", "physiotherapist",
        "pharmacist", "nurse",
    ]

    public_service_keywords = [
        "police", "army", "civil", "officer",
    ]

    if any(keyword in title for keyword in technology_keywords):
        if result.openness >= 60:
            reasons.append(
                "High openness supports analytical thinking and problem solving."
            )

        if result.conscientiousness >= 60:
            reasons.append(
                "Good discipline helps complete complex technical tasks."
            )

        if result.neuroticism <= 45:
            reasons.append(
                "Emotional stability is valuable in technical work."
            )

    elif any(keyword in title for keyword in creative_keywords):
        if result.openness >= 60:
            reasons.append(
                "Your creativity makes you suitable for creative professions."
            )

        if result.extraversion >= 55:
            reasons.append(
                "Communication skills help creative collaboration."
            )

    elif any(keyword in title for keyword in business_keywords):
        if result.extraversion >= 60:
            reasons.append(
                "High extraversion supports leadership and communication."
            )

        if result.agreeableness >= 60:
            reasons.append(
                "Good teamwork ability is important in management."
            )

    elif any(keyword in title for keyword in medical_keywords):
        if result.agreeableness >= 60:
            reasons.append(
                "Empathy is important in healthcare professions."
            )

        if result.conscientiousness >= 60:
            reasons.append(
                "Attention to detail supports patient care."
            )

    elif any(keyword in title for keyword in public_service_keywords):
        if result.conscientiousness >= 60:
            reasons.append(
                "Discipline is essential in public service."
            )

        if result.neuroticism <= 45:
            reasons.append(
                "Stress management helps in high-pressure environments."
            )

    if not reasons:
        reasons.append(
            "Your overall personality profile aligns well with this career."
        )

    return reasons[:3]


def generate_ai_warning(result, career):
    """Generate areas that may reduce compatibility with a career."""

    warnings = []

    if result.openness < career.min_openness:
        warnings.append(
            "Creativity score is slightly below the preferred level."
        )

    if result.conscientiousness < career.min_conscientiousness:
        warnings.append(
            "Discipline could be improved."
        )

    if result.extraversion < career.min_extraversion:
        warnings.append(
            "Communication skills can be strengthened."
        )

    if result.agreeableness < career.min_agreeableness:
        warnings.append(
            "Teamwork ability may need improvement."
        )

    if result.neuroticism > career.max_neuroticism:
        warnings.append(
            "Better stress management would improve compatibility."
        )

    return warnings[:2]