from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

from openai import OpenAI

from assessment.models import AssessmentResult
from recommendations.recommendation_engine import get_recommended_careers

import json


client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=settings.OPENROUTER_API_KEY
)


def chatbot_home(request):
    return render(request, "chatbot/chatbot.html")


@csrf_exempt
def chatbot_api(request):

    if request.method != "POST":
        return JsonResponse({
            "reply": "Invalid Request"
        })

    try:

        data = json.loads(request.body)
        message = data.get("message", "").strip()

        greetings = [
            "hi",
            "hello",
            "hey",
            "hii",
            "hy",
            "salam",
            "assalam o alaikum",
            "assalamu alaikum",
            "good morning",
            "good afternoon",
            "good evening"
        ]

        if message.lower() in greetings:
            return JsonResponse({
                "reply": (
                    "👋 Hello! I'm your AI Career Assistant.\n\n"
                    "Ask me anything about your personality assessment or career recommendations."
                )
            })

        if (
            not message
            or message in [".", "..", "...", "....", "....."]
        ):
            return JsonResponse({
                "reply": (
                    "👋 Please ask a career-related question."
                )
            })

        # Get latest personality assessment result
        result = AssessmentResult.objects.filter(
            session__user=request.user
        ).order_by("-created_at").first()

        career_info = ""

        if result:

            careers = get_recommended_careers(
                result,
                top_n=5
            )

            career_info = f"""
Student Personality Scores:

Openness: {result.openness}
Conscientiousness: {result.conscientiousness}
Extraversion: {result.extraversion}
Agreeableness: {result.agreeableness}
Neuroticism: {result.neuroticism}

Recommended Careers:
"""

            if careers:

                for career in careers:

                    career_info += f"""

Career: {career.get('title', 'Unknown')}

Category: {career.get('category', 'N/A')}

Final Recommendation Score: {career.get('final_score', 'N/A')}%

Machine Learning Score: {career.get('ml_score', 'N/A')}%

Personality Match Score: {career.get('rule_score', 'N/A')}%

Match Level: {career.get('match_label', 'N/A')}

Description:
{career.get('description', 'No description')}

Required Personality Traits:
{career.get('required_traits', 'N/A')}

Required Skills:
{career.get('skills', 'No skills')}

Why Recommended:
{career.get('reasons', 'No reasons')}

Areas to Improve:
{career.get('warnings', 'None')}

Learning Roadmap:
{career.get('roadmap', 'No roadmap available')}

--------------------------------------------------------

"""

        else:

            career_info = """
No personality assessment result found.
Ask the student to complete the personality assessment first.
"""

        prompt = f"""
You are an AI Career Assistant for a Personality Assessment System.

Student Information:

{career_info}

Student Question:

{message}

Instructions:

- Answer ONLY the user's question.
- Keep the answer between 40 and 60 words.
- Use very simple English.
- Do NOT use headings.
- Do NOT use bullet points unless the user asks.
- Explain the reason in 2-3 short sentences.
- Mention only the most important personality traits.
- End with one short suggestion.
- Never give unnecessary details.
"""

        response = client.chat.completions.create(

            model="nvidia/nemotron-3-ultra-550b-a55b:free",

            messages=[
                {
                    "role": "system",
                    "content": "You are a professional AI career counselor."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        reply = response.choices[0].message.content

        if not reply:
            reply = "Sorry, I could not generate a response."

        return JsonResponse({
            "reply": reply
        })

    except Exception as e:

        return JsonResponse({
            "reply": f"Error: {str(e)}"
        })