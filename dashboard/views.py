"""
User dashboard analytics.
"""

from collections import Counter

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from assessment.models import AssessmentResult
from recommendations.ai_personality import generate_personality_type
from recommendations.models import AIModelStatus
from recommendations.recommendation_engine import get_recommended_careers


@login_required
def dashboard_home(request):
    """Display the authenticated user's analytics dashboard."""

    results = list(
        AssessmentResult.objects
        .filter(
            session__user=request.user,
            session__is_completed=True,
        )
        .select_related("session", "session__user")
        .prefetch_related("session__userresponse_set")
        .order_by("-created_at")
    )

    total_assessments = len(results)
    latest_result = results[0] if results else None

    latest_personality_type = "No assessment completed"
    latest_personality_summary = (
        "Complete your first assessment to see your personality profile."
    )
    latest_career = None

    if latest_result:
        (
            latest_personality_type,
            latest_personality_summary,
        ) = generate_personality_type(latest_result)

        latest_recommendations = get_recommended_careers(
            latest_result,
            top_n=1,
        )

        if latest_recommendations:
            latest_career = latest_recommendations[0]

    model_status = AIModelStatus.objects.filter(id=1).first()

    # Oldest to newest order for charts.
    chronological_results = sorted(
        results, key=lambda r: r.created_at
    )

    chart_labels = []
    openness_history = []
    conscientiousness_history = []
    extraversion_history = []
    agreeableness_history = []
    neuroticism_history = []

    for result in chronological_results:
        chart_labels.append(
            result.created_at.strftime("%d %b")
        )
        openness_history.append(result.openness)
        conscientiousness_history.append(result.conscientiousness)
        extraversion_history.append(result.extraversion)
        agreeableness_history.append(result.agreeableness)
        neuroticism_history.append(result.neuroticism)

    latest_radar_scores = []

    if latest_result:
        latest_radar_scores = [
            latest_result.openness,
            latest_result.conscientiousness,
            latest_result.extraversion,
            latest_result.agreeableness,
            latest_result.neuroticism,
        ]

    assessment_history = []
    career_counter = Counter()

    for result in results:
        personality_type, _ = generate_personality_type(result)

        if latest_result and result.id == latest_result.id and latest_career:
            top_career = latest_career
        else:
            top_recommendation = get_recommended_careers(
                result,
                top_n=1,
            )
            top_career = (
                top_recommendation[0]
                if top_recommendation
                else None
            )

        if top_career:
            career_counter[top_career["title"]] += 1

        answered_questions = len(result.session.userresponse_set.all())

        assessment_history.append({
            "result": result,
            "personality_type": personality_type,
            "career": top_career,
            "answered_questions": answered_questions,
            "assessment_date": result.created_at,
        })

    top_careers = career_counter.most_common(5)

    career_labels = [
        career_name
        for career_name, count in top_careers
    ]

    career_values = [
        count
        for career_name, count in top_careers
    ]

    feedback_progress = 0

    if model_status:
        feedback_progress = min(
            (
                model_status.feedback_since_last_training
                / 50
            ) * 100,
            100,
        )

    ai_accuracy = 0

    if model_status:
        ai_accuracy = model_status.current_accuracy

    completed_roadmap_count = 0
    active_goal = None
    logged_today = False
    if request.user.is_authenticated:
        from recommendations.models import UserRoadmapProgress, UserCareerGoal, UserDailyLog
        from django.utils import timezone
        completed_roadmap_count = UserRoadmapProgress.objects.filter(
            user=request.user,
            completed=True
        ).count()
        active_goal = UserCareerGoal.objects.filter(user=request.user, is_active=True).first()
        if active_goal:
            today = timezone.now().date()
            logged_today = UserDailyLog.objects.filter(user=request.user, career_goal=active_goal, date=today, completed=True).exists()

    context = {
        "total_assessments": total_assessments,
        "completed_roadmap_count": completed_roadmap_count,
        "active_goal": active_goal,
        "logged_today": logged_today,
        "latest_result": latest_result,

        "latest_personality_type": latest_personality_type,
        "latest_personality_summary": latest_personality_summary,
        "latest_career": latest_career,
        "model_status": model_status,
        "feedback_progress": round(feedback_progress, 2),
        "ai_accuracy": ai_accuracy,
        "assessment_history": assessment_history,
        "chart_labels": chart_labels,
        "openness_history": openness_history,
        "conscientiousness_history": conscientiousness_history,
        "extraversion_history": extraversion_history,
        "agreeableness_history": agreeableness_history,
        "neuroticism_history": neuroticism_history,
        "latest_radar_scores": latest_radar_scores,
        "career_labels": career_labels,
        "career_values": career_values,
    }

    return render(
        request,
        "dashboard/user_dashboard.html",
        context,
    )