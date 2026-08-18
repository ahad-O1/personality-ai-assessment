"""
AI Mock Interview Views for Personality AI.
Handles session initialization, real-time AJAX answer evaluation,
and post-interview performance dashboard rendering.
"""

import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.urls import reverse

from assessment.models import AssessmentResult
from .models import Career, UserInterviewSession, UserInterviewResponse
from .interview_engine import (
    generate_interview_questions,
    evaluate_interview_answer,
    generate_adaptive_next_question,
    generate_final_interview_report,
)



@login_required
def start_interview_session(request, career_id):
    """
    Initialize or resume an AI Mock Interview session for a specific career.
    """
    user = request.user
    career = get_object_or_404(Career, id=career_id)

    latest_result = AssessmentResult.objects.filter(session__user=user).order_by("-created_at").first()


    # Check for existing in_progress session or create a new one
    session = UserInterviewSession.objects.filter(
        user=user,
        career=career,
        status="in_progress"
    ).first()

    if not session:
        session = UserInterviewSession.objects.create(
            user=user,
            career=career,
            assessment_result=latest_result,
            status="in_progress",
            total_questions=8,
            current_question_index=1,
        )


        questions = generate_interview_questions(career, latest_result)
        for q in questions:
            UserInterviewResponse.objects.create(
                session=session,
                question_number=q["question_number"],
                stage=q["stage"],
                question_text=q["question_text"],
            )

    # Get current active response
    current_response = UserInterviewResponse.objects.filter(
        session=session,
        question_number=session.current_question_index
    ).first()

    if not current_response:
        # If all questions answered, finish and view report
        generate_final_interview_report(session)
        return redirect(f"/recommendations/interview/report/{session.id}/")


    context = {
        "session": session,
        "career": career,
        "current_response": current_response,
        "total_questions": session.total_questions,
    }
    return render(request, "recommendations/interview_room.html", context)


@login_required
@csrf_exempt
def submit_interview_answer(request, session_id):
    """
    AJAX endpoint to receive user's text/speech answer, compute 4-metric AI scores,
    and return instant feedback + next question data.
    """
    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=400)

    try:
        session = get_object_or_404(UserInterviewSession, id=session_id, user=request.user)
        data = json.loads(request.body)
        user_answer = data.get("answer", "").strip()

        current_response = UserInterviewResponse.objects.filter(
            session=session,
            question_number=session.current_question_index
        ).first()

        if not current_response:
            return JsonResponse({"error": "Question response record not found."}, status=404)

        # Run 4-Metric Evaluation
        eval_result = evaluate_interview_answer(
            career=session.career,
            question_text=current_response.question_text,
            stage=current_response.stage,
            user_answer=user_answer
        )

        # Save evaluation on current response
        current_response.user_answer = user_answer
        current_response.accuracy_score = eval_result["accuracy_score"]
        current_response.clarity_score = eval_result["clarity_score"]
        current_response.confidence_score = eval_result["confidence_score"]
        current_response.structure_score = eval_result["structure_score"]
        current_response.overall_question_score = eval_result["overall_question_score"]
        current_response.feedback_notes = eval_result["feedback_notes"]
        current_response.ideal_answer = eval_result["ideal_answer"]
        current_response.save()

        # Advance session to next question
        session.current_question_index += 1
        session.save()

        # Check if interview complete
        if session.current_question_index > session.total_questions:
            session.completed_at = timezone.now()
            session.save()
            generate_final_interview_report(session)

            return JsonResponse({
                "completed": True,
                "redirect_url": f"/recommendations/interview/report/{session.id}/",
                "evaluation": eval_result,
            })


        # Fetch next question data & adapt dynamically live!
        next_response = UserInterviewResponse.objects.filter(
            session=session,
            question_number=session.current_question_index
        ).first()

        if next_response:
            adaptive_q = generate_adaptive_next_question(session, current_response, user_answer)
            next_response.question_text = adaptive_q
            next_response.save()

        return JsonResponse({
            "completed": False,
            "evaluation": eval_result,
            "next_question": {
                "question_number": next_response.question_number,
                "stage": next_response.stage,
                "stage_display": f"Stage {1 if next_response.stage == 'HR' else (2 if next_response.stage == 'TECHNICAL' else 3)}: {next_response.get_stage_display()}",
                "question_text": next_response.question_text,
            }
        })


    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
def interview_summary_report(request, session_id):
    """
    Render post-interview performance dashboard report.
    """
    session = get_object_or_404(UserInterviewSession, id=session_id, user=request.user)

    if session.status != "completed":
        generate_final_interview_report(session)

    responses = session.responses.all().order_by("question_number")

    context = {
        "session": session,
        "career": session.career,
        "responses": responses,
    }
    return render(request, "recommendations/interview_report.html", context)
