import json
import logging
from typing import Any, cast
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from openai import OpenAI

from assessment.models import AssessmentResult
from recommendations.recommendation_engine import get_recommended_careers
from recommendations.ai_personality import generate_personality_type, generate_strengths
from .models import ChatMessage

logger = logging.getLogger(__name__)


def chatbot_home(request):
    return render(request, "chatbot/chatbot.html")


def safe_val(obj, key, default=""):
    """Bulletproof helper to extract dictionary keys or model attributes safely."""
    if not obj:
        return default
    if isinstance(obj, dict):
        val = obj.get(key, default)
        return val if val is not None else default
    val = getattr(obj, key, default)
    return val if val is not None else default


def generate_smart_local_reply(message, result, careers, personality_type, strengths):
    """
    Enterprise-grade, structured local response generator for Roman Urdu and English.
    Strictly zero-emoji and zero-asterisk raw markdown policy for clean professional formatting.
    """
    msg_lower = message.lower()
    
    top_c_obj = careers[0] if (careers and len(careers) > 0) else None
    top_career_title = safe_val(top_c_obj, "title", "Software Engineer")
    top_career_score = safe_val(top_c_obj, "final_score", 85)
    top_career_skills = safe_val(top_c_obj, "skills", "Python, SQL, Data Modeling")

    c2_obj = careers[1] if (careers and len(careers) > 1) else None
    career_2 = safe_val(c2_obj, "title", "Data Analyst")

    c3_obj = careers[2] if (careers and len(careers) > 2) else None
    career_3 = safe_val(c3_obj, "title", "AI Engineer")

    # 1. ROMAN URDU DETECTION
    is_roman_urdu = any(w in msg_lower for w in [
        "kon", "konsa", "konsi", "kya", "kaise", "kesa", "kaisa", "kis", "mera", "meri", 
        "mere", "mujhe", "mujh", "hona", "chayia", "chahiye", "jana", "match", "karne", 
        "karu", "karoon", "batao", "bataen", "salam", "sahi", "karo", "maian", "kaun", "kn", "sy"
    ])

    if is_roman_urdu:
        if any(w in msg_lower for w in ["career", "careerer", "match", "kaun", "konsa", "konsi", "jana", "hona", "kn"]):
            return (
                f"Recommended Career Analysis:\n\n"
                f"Aap ke profile aur assessment results ke hisaab se sab se best career options:\n\n"
                f"1. {top_career_title} ({top_career_score}% Fit) — Sab se Highest Match\n"
                f"2. {career_2} — Strong Technical Alignment\n"
                f"3. {career_3} — High Analytical Fit\n\n"
                f"Mashwara: Aap ko {top_career_title} ki taraf jana chahiye kyunke aap ke personality assessment scores ({personality_type}) is role se sab se ziada align karte hain."
            )
        elif any(w in msg_lower for w in ["skill", "sikho", "seekho", "seekhoon", "kya seekho"]):
            return (
                f"Required Skillsets for {top_career_title}:\n\n"
                f"1. Core Fundamentals & System Design\n"
                f"2. {top_career_skills}\n"
                f"3. Practical Portfolio Projects & Code Optimization\n\n"
                f"Aap in skills ko step-by-step seekhne ke liye humare Visual Roadmap Module ko follow kar sakte hain."
            )
        elif any(w in msg_lower for w in ["score", "result", "test", "report"]):
            return (
                f"Assessment Profile Summary:\n\n"
                f"Personality Archetype: {personality_type}\n"
                f"Primary Strengths: {', '.join(strengths[:2]) if strengths else 'Analytical Thinking'}\n"
                f"Primary Target Role: {top_career_title} ({top_career_score}% Fit)"
            )
        else:
            return (
                f"AI Career Advisor:\n\n"
                f"Aap ke assessment result ke mutabiq aap ke liye sab se suitable career {top_career_title} hai ({top_career_score}% Match).\n\n"
                f"Aap is role ke bare mein koi bhi technical ya career query pooch sakte hain."
            )

    # 2. ENGLISH CAREER QUESTIONS
    if any(w in msg_lower for w in ["career", "job", "role", "match", "best", "recommend"]):
        return (
            f"Top Recommended Careers:\n\n"
            f"1. {top_career_title} ({top_career_score}% Fit)\n"
            f"2. {career_2}\n"
            f"3. {career_3}\n\n"
            f"Your personality archetype ({personality_type}) demonstrates high suitability for this profile."
        )
    elif any(w in msg_lower for w in ["skill", "learn", "study"]):
        return (
            f"Key Skills for {top_career_title}:\n\n"
            f"1. {top_career_skills}\n"
            f"2. System Architecture & Practical Projects\n"
            f"3. Technical Communication"
        )
    else:
        return (
            f"AI Career Advisor:\n\n"
            f"Your top matched role is {top_career_title} ({top_career_score}% match score).\n\n"
            f"Feel free to ask specific questions about your assessment or skills to master."
        )


@csrf_exempt
def chatbot_api(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid Request"})

    try:
        data = json.loads(request.body)
        message = data.get("message", "").strip()

        greetings = [
            "hi", "hello", "hey", "hii", "hy", "salam",
            "assalam o alaikum", "assalamu alaikum",
            "good morning", "good afternoon", "good evening"
        ]

        # Get latest personality assessment result (with guest fallback)
        result = None
        if request.user.is_authenticated:
            result = AssessmentResult.objects.filter(
                session__user=request.user
            ).order_by("-created_at").first()

        if not result:
            result = AssessmentResult.objects.order_by("-created_at").first()

        careers = get_recommended_careers(result, top_n=3) if result else []
        personality_type, _ = generate_personality_type(result) if result else ("Balanced Personality", "")
        strengths = generate_strengths(result) if result else ["Problem Solving"]

        top_c_obj = careers[0] if (careers and len(careers) > 0) else None
        top_career_title = safe_val(top_c_obj, "title", "Software Engineer")

        if message.lower() in greetings:
            return JsonResponse({
                "reply": (
                    f"Welcome to AI Career Advisor\n\n"
                    f"Your primary career match is {top_career_title}.\n\n"
                    f"Ask any question regarding your assessment scores, skill roadmaps, or top career recommendations."
                )
            })

        if not message or message in [".", "..", "...", "...."]:
            return JsonResponse({
                "reply": "Please enter a valid question or response."
            })

        # Save user message if authenticated
        if request.user.is_authenticated:
            ChatMessage.objects.create(
                user=request.user,
                sender="user",
                message=message
            )

        career_info = ""
        if result:
            career_info = f"Personality Scores: O:{result.openness}%, C:{result.conscientiousness}%, E:{result.extraversion}%, A:{result.agreeableness}%, N:{result.neuroticism}%\n"
            if careers:
                career_info += "Top Recommended Careers:\n"
                for c in careers:
                    career_info += f"- {safe_val(c, 'title', 'Career')}: {safe_val(c, 'final_score', 80)}% Match ({safe_val(c, 'match_label', 'Match')}). Skills: {safe_val(c, 'skills', '')}\n"

        # Try OpenRouter API with short timeout
        api_key = getattr(settings, "OPENROUTER_API_KEY", None)
        reply = None

        if api_key:
            try:
                system_prompt = (
                    f"You are a professional AI Career Counselor.\nStudent Profile:\n{career_info}\n"
                    f"Do NOT output raw markdown asterisks (**) or star characters in your text. Provide clean professional text with plain numbered lists (1., 2., 3.) and clean paragraph spacing. If the user asks in Roman Urdu, respond in clear professional Roman Urdu."
                )

                messages_payload: list[dict[str, str]] = [{"role": "system", "content": system_prompt}]

                if request.user.is_authenticated:
                    recent_history = ChatMessage.objects.filter(user=request.user).order_by("-created_at")[:4]
                    for h in reversed(recent_history):
                        role = "user" if h.sender == "user" else "assistant"
                        messages_payload.append({"role": role, "content": h.message})
                else:
                    messages_payload.append({"role": "user", "content": message})

                client = OpenAI(
                    base_url="https://openrouter.ai/api/v1",
                    api_key=api_key,
                    timeout=3.5
                )
                response = client.chat.completions.create(
                    model="nvidia/nemotron-3-ultra-550b-a55b:free",
                    messages=cast(Any, messages_payload),
                    max_tokens=220
                )
                reply = response.choices[0].message.content.strip()
            except Exception as e:
                logger.warning(f"OpenAI API failed, switching to local smart engine: {e}")
                reply = None

        # Fallback to Local Smart Engine if OpenRouter is slow/unavailable
        if not reply:
            reply = generate_smart_local_reply(
                message=message,
                result=result,
                careers=careers,
                personality_type=personality_type,
                strengths=strengths
            )

        # Save assistant message
        if request.user.is_authenticated:
            ChatMessage.objects.create(
                user=request.user,
                sender="assistant",
                message=reply
            )

        return JsonResponse({"reply": reply})

    except Exception as e:
        logger.error(f"Chatbot API top-level error: {e}")
        return JsonResponse({
            "reply": "AI Career Advisor: Your top recommended career match is Software Engineer (or Data Analyst). Feel free to ask any questions regarding your assessment."
        })