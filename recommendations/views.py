"""
Recommendations views for career scoring, roadmap tracking, and reminders.
"""

import json
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from django.db import models
from assessment.models import AssessmentResult
from .models import Career, UserRoadmapProgress, UserCareerGoal, UserDailyLog
from .ai_personality import (
    generate_improvements,
    generate_personality_details,
    generate_personality_type,
    generate_strengths,
    get_personality_analysis,
)
from .recommendation_engine import get_recommended_careers
from .roadmap import generate_structured_roadmap
from django.utils import timezone


def recommend_careers(request, result_id):
    """Display personality analysis and career recommendations with interactive roadmaps."""

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

    # Attach interactive roadmap progress
    completed_steps_map = {}
    if request.user.is_authenticated:
        progress_qs = UserRoadmapProgress.objects.filter(
            user=request.user,
            completed=True
        )
        for p in progress_qs:
            if p.career_id not in completed_steps_map:
                completed_steps_map[p.career_id] = set()
            completed_steps_map[p.career_id].add(p.step_index)

    for career_dict in careers:
        cid = career_dict.get("id")
        completed_steps = completed_steps_map.get(cid, set())
        struct_nodes = career_dict.get("structured_roadmap", [])
        raw_roadmap = career_dict.get("roadmap", [])
        enriched_roadmap = []

        for idx, step_text in enumerate(raw_roadmap):
            node_data = struct_nodes[idx] if idx < len(struct_nodes) else {}
            yt_url = node_data.get("youtube_url", "https://www.youtube.com/watch?v=kqtD5dpn9C8")
            yt_embed = node_data.get("youtube_embed_url", "https://www.youtube-nocookie.com/embed/kqtD5dpn9C8?rel=0")
            enriched_roadmap.append({
                "index": idx,
                "text": step_text,
                "completed": idx in completed_steps,
                "subtopics": node_data.get("subtopics", []),
                "youtube_url": yt_url,
                "youtube_embed_url": yt_embed,
                "youtube_channel": node_data.get("youtube_channel", "freeCodeCamp.org"),
                "duration": node_data.get("duration", "2-4 Weeks"),
                "resource": node_data.get("resource", "Video Courses & Docs"),
            })
        career_dict["enriched_roadmap"] = enriched_roadmap



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


@login_required
@csrf_exempt
def toggle_roadmap_step(request):
    """AJAX endpoint to toggle learning roadmap step completion."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        data = json.loads(request.body)
        career_id = data.get("career_id")
        step_index = int(data.get("step_index"))

        career = get_object_or_404(Career, id=career_id)

        progress_obj, created = UserRoadmapProgress.objects.get_or_create(
            user=request.user,
            career=career,
            step_index=step_index,
            defaults={"completed": True}
        )
        if not created:
            progress_obj.completed = not progress_obj.completed
            progress_obj.save()

        return JsonResponse({
            "success": True,
            "career_id": career_id,
            "step_index": step_index,
            "completed": progress_obj.completed
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def compare_careers(request, result_id):
    """Side-by-side comparison view of top recommended careers."""
    result = get_object_or_404(AssessmentResult, id=result_id)
    careers = get_recommended_careers(result, top_n=3)

    personality_type, _ = generate_personality_type(result)

    context = {
        "result": result,
        "careers": careers,
        "personality_type": personality_type,
    }
    return render(request, "recommendations/career_comparison.html", context)


@login_required
def select_career_goal(request, career_id):
    """Set a career as the user's primary active tracking goal."""
    career = get_object_or_404(Career, id=career_id)

    # Deactivate any previous active goals for this user
    UserCareerGoal.objects.filter(user=request.user, is_active=True).update(is_active=False)

    goal, created = UserCareerGoal.objects.get_or_create(
        user=request.user,
        career=career,
        defaults={"is_active": True, "streak_count": 0}
    )
    if not created:
        goal.is_active = True
        goal.save()

    return redirect("career_tracker_dashboard")


@login_required
def career_tracker_dashboard(request):
    """Dedicated tracker dashboard for daily learning progress, milestones, and streak."""
    user = request.user

    # Get current active goal or pick latest recommendation
    active_goal = UserCareerGoal.objects.filter(user=user, is_active=True).first()

    if not active_goal:
        active_goal = UserCareerGoal.objects.filter(user=user).first()
        if active_goal:
            active_goal.is_active = True
            active_goal.save()

    if not active_goal:
        latest_result = AssessmentResult.objects.filter(user=user).order_by("-created_at").first()
        if latest_result:
            careers = get_recommended_careers(latest_result, top_n=1)
            if careers:
                top_career_obj = Career.objects.filter(id=careers[0]["id"]).first()
                if top_career_obj:
                    active_goal = UserCareerGoal.objects.create(
                        user=user,
                        career=top_career_obj,
                        is_active=True
                    )

    all_goals = UserCareerGoal.objects.filter(user=user).select_related("career")

    if not active_goal:
        return render(request, "recommendations/tracker.html", {
            "no_goal": True,
            "all_goals": all_goals,
        })

    career = active_goal.career
    structured_roadmap = generate_structured_roadmap(career)

    completed_steps = set(
        UserRoadmapProgress.objects.filter(
            user=user, career=career, completed=True
        ).values_list("step_index", flat=True)
    )

    total_steps = len(structured_roadmap) if structured_roadmap else 6
    completed_count = len(completed_steps)
    progress_percentage = int((completed_count / total_steps) * 100) if total_steps > 0 else 0

    enriched_nodes = []
    for node in structured_roadmap:
        idx = node["index"]
        enriched_nodes.append({
            **node,
            "completed": idx in completed_steps
        })

    today = timezone.now().date()
    today_log = UserDailyLog.objects.filter(user=user, career_goal=active_goal, date=today).first()
    logged_today = bool(today_log and today_log.completed)

    recent_logs = UserDailyLog.objects.filter(
        user=user, career_goal=active_goal
    ).order_by("-date")[:14]

    total_minutes_spent = UserDailyLog.objects.filter(
        user=user, career_goal=active_goal
    ).aggregate(total=models.Sum("study_duration_minutes"))["total"] or 0

    context = {
        "active_goal": active_goal,
        "all_goals": all_goals,
        "career": career,
        "structured_roadmap": enriched_nodes,
        "progress_percentage": progress_percentage,
        "completed_count": completed_count,
        "total_steps": total_steps,
        "today_log": today_log,
        "logged_today": logged_today,
        "recent_logs": recent_logs,
        "total_minutes_spent": total_minutes_spent,
        "streak_count": active_goal.streak_count,
        "no_goal": False,
    }

    return render(request, "recommendations/tracker.html", context)


@login_required
@csrf_exempt
def log_daily_progress(request):
    """AJAX endpoint to record today's daily learning log and update streak."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        data = json.loads(request.body)
        goal_id = data.get("goal_id")
        minutes = int(data.get("minutes", 30))
        notes = data.get("notes", "").strip()

        user = request.user
        if goal_id:
            goal = get_object_or_404(UserCareerGoal, id=goal_id, user=user)
        else:
            goal = UserCareerGoal.objects.filter(user=user, is_active=True).first()
            if not goal:
                return JsonResponse({"error": "No active career goal found"}, status=404)

        today = timezone.now().date()
        daily_log, created = UserDailyLog.objects.get_or_create(
            user=user,
            career_goal=goal,
            date=today,
            defaults={
                "study_duration_minutes": minutes,
                "notes": notes,
                "completed": True
            }
        )
        if not created:
            daily_log.study_duration_minutes = minutes
            daily_log.notes = notes
            daily_log.completed = True
            daily_log.save()

        last_date = goal.last_active_date
        if last_date != today:
            if last_date and (today - last_date).days == 1:
                goal.streak_count += 1
            elif not last_date or (today - last_date).days > 1:
                goal.streak_count = 1
            goal.last_active_date = today
            goal.save()

        return JsonResponse({
            "success": True,
            "streak_count": goal.streak_count,
            "date": str(today),
            "study_duration_minutes": daily_log.study_duration_minutes,
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@csrf_exempt
def update_reminder_settings(request):
    """AJAX endpoint to update daily reminder preferences."""
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)
    try:
        data = json.loads(request.body)
        goal_id = data.get("goal_id")
        enabled = bool(data.get("enabled", True))
        reminder_time = data.get("reminder_time", "20:00")

        goal = get_object_or_404(UserCareerGoal, id=goal_id, user=request.user)
        goal.daily_reminder_enabled = enabled
        goal.reminder_time = reminder_time
        goal.save()

        return JsonResponse({
            "success": True,
            "enabled": enabled,
            "reminder_time": reminder_time
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def check_daily_reminder(request):
    """
    Check if the authenticated user has an active career goal due for a reminder.
    Returns JSON status so frontend JS can trigger a live popup notification.
    """
    user = request.user
    active_goal = UserCareerGoal.objects.filter(
        user=user,
        is_active=True,
        daily_reminder_enabled=True
    ).first()

    if not active_goal:
        return JsonResponse({"due": False})

    today = timezone.now().date()
    logged_today = UserDailyLog.objects.filter(
        user=user,
        career_goal=active_goal,
        date=today,
        completed=True
    ).exists()

    if logged_today:
        return JsonResponse({"due": False, "logged_today": True})

    current_time_str = timezone.localtime().strftime("%H:%M")
    reminder_time_str = active_goal.reminder_time or "20:00"

    is_due = current_time_str >= reminder_time_str

    return JsonResponse({
        "due": is_due,
        "logged_today": False,
        "goal_id": active_goal.id,
        "career_title": active_goal.career.title,
        "streak_count": active_goal.streak_count,
        "reminder_time": reminder_time_str,
        "current_time": current_time_str,
    })