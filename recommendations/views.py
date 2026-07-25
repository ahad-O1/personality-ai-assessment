"""
Main web views for career recommendations.
"""

from django.shortcuts import get_object_or_404, render

from assessment.models import AssessmentResult

from .ai_personality import (
    generate_improvements,
    generate_personality_details,
    generate_personality_type,
    generate_strengths,
    get_personality_analysis,
)
from .recommendation_engine import get_recommended_careers


def recommend_careers(request, result_id):
    """Display personality analysis and career recommendations."""

    result = get_object_or_404(
        AssessmentResult,
        id=result_id,
    )

    careers = get_recommended_careers(result)
    personality_analysis = get_personality_analysis(result)

    personality_type, personality_summary = (
        generate_personality_type(result)
    )

    personality_details = generate_personality_details(result)
    strengths = generate_strengths(result)
    improvements = generate_improvements(result)

    context = {
        "result": result,
        "careers": careers,
        "personality_analysis": personality_analysis,
        "personality_type": personality_type,
        "personality_summary": personality_summary,
        "personality_details": personality_details,
        "strengths": strengths,
        "improvements": improvements,
    }

    return render(
        request,
        "recommendations/careers.html",
        context,
    )