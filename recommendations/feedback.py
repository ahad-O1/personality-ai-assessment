"""
Career feedback views.

This module:
1. Saves or updates career feedback.
2. Counts valid unused feedback.
3. Updates AI model status.
4. Automatically triggers retraining when the threshold is reached.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from django.views.decorators.http import require_POST

from assessment.models import AssessmentResult

from .auto_retraining import trigger_automatic_retraining
from .models import AIModelStatus, Career, CareerFeedback


@login_required
@require_POST
def submit_career_feedback(request, result_id):
    """
    Save or update feedback for a recommended career.

    Valid training feedback means:
    - career is marked relevant
    - rating is 4 or 5
    - feedback has not already been used for training
    """

    result = get_object_or_404(
        AssessmentResult,
        id=result_id,
        session__user=request.user,
    )

    career_id = request.POST.get("career_id")
    rating = request.POST.get("rating")
    comments = request.POST.get("comments", "").strip()
    is_relevant = request.POST.get("is_relevant") == "yes"

    career = get_object_or_404(
        Career,
        id=career_id,
        is_active=True,
    )

    try:
        rating_value = int(rating)
    except (TypeError, ValueError):
        messages.error(
            request,
            "Please select a valid rating.",
        )
        return redirect(
            "recommend_careers",
            result_id=result.id,
        )

    if rating_value not in range(1, 6):
        messages.error(
            request,
            "Rating must be between 1 and 5.",
        )
        return redirect(
            "recommend_careers",
            result_id=result.id,
        )

    # Save new feedback or update existing feedback.
    CareerFeedback.objects.update_or_create(
        user=request.user,
        assessment_result=result,
        career=career,
        defaults={
            "rating": rating_value,
            "is_relevant": is_relevant,
            "comments": comments,
            "used_for_training": False,
        },
    )

    # Count only valid feedback that has not yet been used
    # for model retraining.
    valid_unused_feedback_count = CareerFeedback.objects.filter(
        is_relevant=True,
        rating__gte=4,
        used_for_training=False,
    ).count()

    # Create the AI model status record automatically
    # if it does not exist yet.
    status, _ = AIModelStatus.objects.get_or_create(
        id=1,
        defaults={
            "model_version": "1.0",
            "current_accuracy": 77.01,
            "previous_accuracy": 76.62,
            "feedback_since_last_training": 0,
            "retraining_running": False,
        },
    )

    # Keep the counter synchronized with actual valid,
    # unused feedback records.
    status.feedback_since_last_training = valid_unused_feedback_count
    status.save(
        update_fields=["feedback_since_last_training"]
    )

    # Start automatic retraining only when the configured
    # feedback threshold has been reached.
    retraining_started = trigger_automatic_retraining()

    if retraining_started:
        messages.success(
            request,
            (
                "Your feedback was saved. Enough new feedback has been "
                "collected, so automatic AI model retraining has started."
            ),
        )
    else:
        messages.success(
            request,
            (
                "Your feedback has been saved for future "
                "AI model improvement."
            ),
        )

    return redirect(
        "recommend_careers",
        result_id=result.id,
    )