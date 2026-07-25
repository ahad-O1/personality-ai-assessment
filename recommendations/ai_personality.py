"""
Personality analysis and summary helpers.
"""


def trait_level(score):
    """Convert a numerical OCEAN score into a readable level."""

    if score >= 70:
        return "High"

    if score >= 40:
        return "Medium"

    return "Low"


def get_personality_analysis(result):
    """Return detailed analysis for the five OCEAN traits."""

    return [
        {
            "trait": "Openness",
            "score": result.openness,
            "level": trait_level(result.openness),
            "description": (
                "Openness reflects creativity, curiosity, imagination, "
                "and interest in learning new ideas."
            ),
        },
        {
            "trait": "Conscientiousness",
            "score": result.conscientiousness,
            "level": trait_level(result.conscientiousness),
            "description": (
                "Conscientiousness shows discipline, organization, "
                "responsibility, and ability to complete tasks."
            ),
        },
        {
            "trait": "Extraversion",
            "score": result.extraversion,
            "level": trait_level(result.extraversion),
            "description": (
                "Extraversion represents social confidence, communication, "
                "energy, and comfort in group situations."
            ),
        },
        {
            "trait": "Agreeableness",
            "score": result.agreeableness,
            "level": trait_level(result.agreeableness),
            "description": (
                "Agreeableness reflects cooperation, empathy, kindness, "
                "and ability to work well with others."
            ),
        },
        {
            "trait": "Neuroticism",
            "score": result.neuroticism,
            "level": trait_level(result.neuroticism),
            "description": (
                "Neuroticism indicates emotional sensitivity, stress response, "
                "nervousness, and mood changes."
            ),
        },
    ]


def generate_personality_type(result):
    """Generate an overall personality type and summary."""

    openness = result.openness
    conscientiousness = result.conscientiousness
    extraversion = result.extraversion
    agreeableness = result.agreeableness
    neuroticism = result.neuroticism

    if openness >= 70 and conscientiousness >= 65:
        return (
            "Innovative Thinker",
            (
                "You enjoy creativity, solving problems, learning new "
                "technologies, and exploring innovative ideas."
            ),
        )

    if extraversion >= 70 and conscientiousness >= 65:
        return (
            "Strategic Leader",
            (
                "You are confident, organized, and naturally capable of "
                "leading people and making decisions."
            ),
        )

    if agreeableness >= 70 and neuroticism <= 45:
        return (
            "Supportive Helper",
            (
                "You are empathetic, cooperative, emotionally balanced, "
                "and enjoy helping others."
            ),
        )

    if openness >= 70 and extraversion >= 70:
        return (
            "Creative Explorer",
            (
                "You enjoy discovering new experiences, expressing ideas, "
                "and communicating with people."
            ),
        )

    if conscientiousness >= 70:
        return (
            "Reliable Planner",
            (
                "You are disciplined, responsible, and capable of "
                "completing tasks efficiently."
            ),
        )

    if neuroticism >= 70:
        return (
            "Sensitive Observer",
            (
                "You notice emotions deeply and respond carefully to "
                "situations. Stress management can further strengthen "
                "your personality."
            ),
        )

    return (
        "Balanced Personality",
        (
            "Your personality is balanced across multiple traits and "
            "allows flexibility in different situations."
        ),
    )


def generate_personality_details(result):
    """Generate characteristics, environments, domains, and summary."""

    strengths = []
    environments = []
    domains = []

    if result.extraversion >= 70:
        strengths += [
            "Confident communication",
            "Leadership potential",
        ]
        environments += [
            "Team-based workplace",
            "Client-facing roles",
        ]
        domains += [
            "Business",
            "Management",
            "Sales",
        ]

    if result.openness >= 60:
        strengths += [
            "Creative thinking",
            "Problem solving",
        ]
        environments += [
            "Creative environment",
            "Innovation-based workplace",
        ]
        domains += [
            "Technology",
            "Creative Media",
            "Research",
        ]

    if result.conscientiousness >= 60:
        strengths += [
            "Discipline",
            "Responsibility",
        ]
        environments += [
            "Structured workplace",
            "Goal-oriented environment",
        ]
        domains += [
            "Technology",
            "Finance",
            "Administration",
        ]

    if result.agreeableness >= 60:
        strengths += [
            "Teamwork",
            "Empathy",
        ]
        environments += [
            "Healthcare",
            "Education",
            "Supportive teams",
        ]
        domains += [
            "Medical",
            "Education",
            "Social Service",
        ]

    if result.neuroticism > 60:
        strengths += [
            "Emotionally aware",
            "Careful decision making",
        ]
        environments += [
            "Calm workplace",
            "Supportive environment",
        ]

    if not strengths:
        strengths = [
            "Balanced thinking",
            "Flexible personality",
        ]

    if not environments:
        environments = [
            "Flexible work environment",
            "Mixed team environment",
        ]

    if not domains:
        domains = [
            "General Management",
            "Technology",
            "Creative Work",
        ]

    summary = (
        "Based on your responses, your personality shows a unique "
        "combination of thinking style, work behavior, emotional pattern, "
        "and social preference. Your recommended careers are selected "
        "using personality scores, AI model prediction, and rule-based "
        "compatibility."
    )

    return {
        "strengths": list(dict.fromkeys(strengths))[:5],
        "environments": list(dict.fromkeys(environments))[:5],
        "domains": list(dict.fromkeys(domains))[:5],
        "summary": summary,
    }


def generate_strengths(result):
    """Generate the user's strongest personality characteristics."""

    strengths = []

    if result.openness >= 60:
        strengths.append("Creative thinking")

    if result.conscientiousness >= 60:
        strengths.append("Discipline and responsibility")

    if result.extraversion >= 60:
        strengths.append("Communication skills")

    if result.agreeableness >= 60:
        strengths.append("Teamwork and empathy")

    if result.neuroticism <= 45:
        strengths.append("Stress control")

    if not strengths:
        strengths.append("Balanced personality")

    return strengths[:5]


def generate_improvements(result):
    """Generate practical areas for personality development."""

    improvements = []

    if result.openness < 60:
        improvements.append("Creativity and idea exploration")

    if result.conscientiousness < 60:
        improvements.append("Time management and consistency")

    if result.extraversion < 60:
        improvements.append("Communication and confidence")

    if result.agreeableness < 60:
        improvements.append("Team collaboration")

    if result.neuroticism > 55:
        improvements.append("Stress management")

    if not improvements:
        improvements.append("Keep improving your existing strengths")

    return improvements[:5]


def get_reliability_level(confidence):
    """Convert confidence percentage into a reliability label."""

    if confidence >= 90:
        return "Very High"

    if confidence >= 75:
        return "High"

    if confidence >= 60:
        return "Medium"

    return "Low"


def get_match_label(score):
    """Convert career compatibility score into a readable label."""

    if score >= 85:
        return "Excellent Match"

    if score >= 70:
        return "Strong Match"

    if score >= 55:
        return "Good Match"

    return "Possible Match"