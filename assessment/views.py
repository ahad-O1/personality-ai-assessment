from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from .models import AssessmentSession, Question, UserResponse, AssessmentResult
from .adaptive_engine import (
    select_next_question,
    get_session_scores,
    average_score,
    MAX_QUESTIONS,
)


@login_required
def start_assessment(request):
    language = request.GET.get("lang", "en")

    session = AssessmentSession.objects.create(user=request.user)

    return redirect(f"/assessment/questions/{session.id}/?lang={language}")


def create_result(session):
    scores, _ = get_session_scores(session)

    result, created = AssessmentResult.objects.get_or_create(
        session=session,
        defaults={
            "openness": average_score(scores["O"]),
            "conscientiousness": average_score(scores["C"]),
            "extraversion": average_score(scores["E"]),
            "agreeableness": average_score(scores["A"]),
            "neuroticism": average_score(scores["N"]),
        }
    )

    if not created:
        result.openness = average_score(scores["O"])
        result.conscientiousness = average_score(scores["C"])
        result.extraversion = average_score(scores["E"])
        result.agreeableness = average_score(scores["A"])
        result.neuroticism = average_score(scores["N"])
        result.save()

    session.is_completed = True
    session.completed_at = timezone.now()
    session.save()

    return result


@login_required
def question_page(request, session_id):
    session = get_object_or_404(
        AssessmentSession,
        id=session_id,
        user=request.user
    )

    language = request.GET.get("lang", request.POST.get("language", "en"))

    if session.is_completed:
        result = get_object_or_404(AssessmentResult, session=session)
        return redirect("recommend_careers", result_id=result.id)

    if request.method == "POST":
        question_id = request.POST.get("question_id")
        answer = request.POST.get("answer")

        if question_id and answer:
            question = get_object_or_404(Question, id=question_id)

            UserResponse.objects.update_or_create(
                session=session,
                question=question,
                defaults={"answer_value": int(answer)}
            )

            question.times_used += 1
            question.save()

        next_question, confidence, trait_confidences = select_next_question(session)

        if next_question is None:
            result = create_result(session)
            return redirect("recommend_careers", result_id=result.id)

        return redirect(f"/assessment/questions/{session.id}/?lang={language}")

    next_question, confidence, trait_confidences = select_next_question(session)

    if next_question is None:
        result = create_result(session)
        return redirect("recommend_careers", result_id=result.id)

    answered_count = UserResponse.objects.filter(session=session).count()

    return render(request, "assessment/question_page.html", {
        "session": session,
        "question": next_question,
        "answered_count": answered_count,
        "max_questions": MAX_QUESTIONS,
        "confidence": confidence,
        "trait_confidences": trait_confidences,
        "language": language,
    })