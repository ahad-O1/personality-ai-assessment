"""
AI Mock Interview Engine for Personality AI.
Handles multi-stage question generation, 4-metric natural language answer scoring,
and comprehensive final performance report synthesis.
"""

from typing import List, Dict, Any


# ============================================================
# DOMAIN QUESTION TEMPLATES & GENERATOR
# ============================================================

import random


def generate_interview_questions(career, assessment_result=None) -> List[Dict[str, Any]]:
    """
    Dynamically generate 5 domain-specific, randomized interview questions tailored to the career role and user profile:
    Stage 1: HR & Behavioral (Q1 & Q2)
    Stage 2: Core Technical & Concepts (Q3 & Q4)
    Stage 3: Situational Scenario (Q5)
    """
    title = career.title
    category = career.category or "Professional Domain"
    skills_list = [s.strip() for s in (career.skills or "").split(",") if s.strip()]
    primary_skills = ", ".join(skills_list[:3]) if skills_list else "core industry tools"
    secondary_skills = ", ".join(skills_list[3:6]) if len(skills_list) > 3 else primary_skills

    # Stage 1: HR & Behavioral Pool (5 Scenarios)
    q1_options = [
        f"Welcome to your mock interview for the {title} role! To begin, please introduce yourself and explain why you are passionate about building a career in {category}, highlighting how your strengths align with this role.",
        f"Welcome! As a candidate for the {title} position, could you walk me through your background, key achievements, and what motivates you to excel in {category}?",
        f"To kick off our session, describe your career journey so far in {category} and explain what specific aspects of the {title} role excite you the most.",
        f"Welcome! What core professional competencies and personal traits make you a strong fit for a high-performance {title} role?",
        f"Thank you for joining today! In your own words, what sets you apart as a candidate for this {title} position, and what unique value do you bring to a team in {category}?"
    ]

    q2_options = [
        f"Describe a challenging situation or complex project in {category} where you faced unexpected obstacles. How did you organize your tasks, collaborate with team members, and deliver a successful outcome?",
        f"In a fast-paced {title} environment, priorities often shift quickly. Can you share an example of how you managed conflicting deadlines while keeping quality high?",
        f"Give an example of a time when you had a difference of opinion with a colleague or lead on a {title} project. How did you handle the situation to achieve a productive outcome?",
        f"Tell me about a time when a project or task in {category} did not go as planned. What was the root cause, what did you learn, and how did you adjust your approach?",
        f"Describe a scenario where you took proactive initiative beyond your assigned responsibilities to solve a critical bottleneck in a {title} project."
    ]

    # Stage 2: Core Technical Concepts Pool (5 Scenarios)
    q3_options = [
        f"As a {title}, working with {primary_skills} is fundamental. What are the key best practices, core architecture, and quality standards you follow when working with these technical skills?",
        f"In your work with {primary_skills}, how do you approach performance optimization, testing, and debugging when dealing with complex features in {category}?",
        f"If you were tasked with setting up a new production workflow using {primary_skills}, what key design decisions and quality standards would you enforce from day one?",
        f"How do you evaluate trade-offs when choosing tools and frameworks like {primary_skills} versus alternative technologies for a scalable {title} solution?",
        f"Walk me through your code/design review process when working with {primary_skills}. How do you ensure maintainability, documentation, and technical debt reduction?"
    ]

    q4_options = [
        f"How do you explain a complex technical concept or analytical problem in {title} to a non-technical client or business manager so they can easily understand its value?",
        f"As a {title}, cross-functional communication is crucial. How do you gather requirements from non-technical stakeholders and translate them into clean technical specifications?",
        f"Imagine a stakeholder requests a feature that is technically inefficient for a {title} project. How would you communicate the risks and propose an alternative solution?",
        f"Describe a situation where you had to present a technical architecture or analytical proposal for {title} to non-technical executives to secure project approval.",
        f"How do you bridge communication gaps between technical developers and non-technical business teams to keep projects aligned with business goals?"
    ]

    # Stage 3: Situational Scenario Pool (5 Scenarios)
    q5_options = [
        f"Imagine a high-priority {title} project deadline is in 48 hours, but a major technical issue or requirement change threatens delivery. Walk me through your step-by-step resolution strategy under pressure.",
        f"Suppose a critical failure or bug occurs in production for a {title} system after release. What is your immediate crisis response plan from discovery to resolution and post-mortem?",
        f"Imagine you are assigned a complex {title} project using tools like {secondary_skills} under tight deadlines. How would you quickly upskill and execute the deliverable successfully?",
        f"Imagine a key team member becomes unavailable right before a major {title} milestone. How would you re-allocate responsibilities and adjust workflows to meet the deliverable on time?",
        f"Suppose client scope-creep threatens to expand project requirements beyond schedule limits for a {title} project. How would you manage scope while delivering core MVP features successfully?"
    ]


    # Return 8 Comprehensive Interview Questions
    questions = [
        {"question_number": 1, "stage": "HR", "stage_display": "Stage 1: HR & Behavioral", "question_text": random.choice(q1_options)},
        {"question_number": 2, "stage": "HR", "stage_display": "Stage 1: HR & Behavioral", "question_text": random.choice(q2_options)},
        {"question_number": 3, "stage": "HR", "stage_display": "Stage 1: HR & Behavioral", "question_text": random.choice([
            f"In a fast-paced {title} environment, priorities often shift quickly. Can you share an example of how you managed conflicting deadlines while keeping quality high?",
            f"Give an example of a time when you had a difference of opinion with a colleague or lead on a {title} project. How did you handle the situation to achieve a productive outcome?"
        ])},
        {"question_number": 4, "stage": "TECHNICAL", "stage_display": "Stage 2: Technical & Concepts", "question_text": random.choice(q3_options)},
        {"question_number": 5, "stage": "TECHNICAL", "stage_display": "Stage 2: Technical & Concepts", "question_text": random.choice([
            f"In your work with {primary_skills}, how do you approach performance optimization, testing, and debugging when dealing with complex features in {category}?",
            f"Walk me through your code/design review process when working with {primary_skills}. How do you ensure maintainability, documentation, and technical debt reduction?"
        ])},
        {"question_number": 6, "stage": "TECHNICAL", "stage_display": "Stage 2: Technical & Concepts", "question_text": random.choice(q4_options)},
        {"question_number": 7, "stage": "SITUATIONAL", "stage_display": "Stage 3: Situational Scenario", "question_text": random.choice(q5_options)},
        {"question_number": 8, "stage": "SITUATIONAL", "stage_display": "Stage 3: Situational Scenario", "question_text": random.choice([
            f"Suppose a critical failure or bug occurs in production for a {title} system after release. What is your immediate crisis response plan from discovery to resolution and post-mortem?",
            f"Imagine you are assigned a complex {title} project using tools like {secondary_skills} under tight deadlines. How would you quickly upskill and execute the deliverable successfully?"
        ])},
    ]

def generate_adaptive_next_question(session, previous_response, user_answer: str) -> str:
    """
    Real-Time Adaptive AI Question Generator:
    Analyzes the user's live answer text and candidate context to dynamically formulate
    the NEXT customized follow-up question.
    """
    career_title = session.career.title
    skills = session.career.skills or "relevant domain tools"
    skills_list = [s.strip() for s in skills.split(",") if s.strip()]
    primary = skills_list[0] if skills_list else "core tools"
    
    clean_text = (user_answer or "").strip()
    next_q_num = session.current_question_index
    lower_text = clean_text.lower()

    # Topic detectors from candidate's previous response
    mentioned_ml = any(w in lower_text for w in ["machine learning", "ml", "ai", "model", "prediction", "data", "deep learning"])
    mentioned_web = any(w in lower_text for w in ["web", "django", "python", "api", "backend", "frontend", "database", "sql", "react", "html", "css"])
    mentioned_team = any(w in lower_text for w in ["team", "collaboration", "lead", "client", "agile", "scrum", "project", "member"])
    mentioned_debug = any(w in lower_text for w in ["test", "debug", "bug", "error", "obstacle", "issue", "problem", "mushkil"])

    if next_q_num == 2:
        if mentioned_ml:
            return f"You highlighted your interest in AI and Data Models. In a {career_title} role, how do you approach data preprocessing, feature engineering, and model evaluation under real-world production conditions?"
        elif mentioned_web:
            return f"Since you emphasized web systems and backend development, how do you approach REST API architecture, database indexing, and application security for a high-traffic {career_title} system?"
        elif mentioned_team:
            return f"Collaboration is essential for a {career_title}. Could you share an example of a project where you collaborated with cross-functional members to overcome a major unexpected bottleneck?"
        else:
            return f"Thanks for sharing! Building on your background, what has been the single most complex technical challenge you solved in {career_title}, and how did you verify your solution?"

    elif next_q_num == 3:
        if mentioned_team:
            return f"When working with cross-functional teams in {career_title}, how do you handle technical disagreements or conflicting architectural priorities among developers?"
        else:
            return f"In a fast-paced {career_title} environment, priorities shift rapidly. How do you organize conflicting deadlines while maintaining top code/design quality?"

    elif next_q_num == 4:
        return f"As a {career_title}, working with tools like {skills} is central. What specific best practices, architecture patterns, and quality standards do you enforce from day one?"

    elif next_q_num == 5:
        if mentioned_debug:
            return f"You mentioned testing and debugging! What specific profiling tools and debugging methodologies do you use when isolating memory leaks or performance bottlenecks in {career_title} systems?"
        else:
            return f"How do you approach performance optimization and query tuning when dealing with large datasets or heavy feature workflows in {career_title}?"

    elif next_q_num == 6:
        return f"How do you communicate complex technical decisions or architectural trade-offs in {career_title} to non-technical business managers or clients so they understand the business ROI?"

    elif next_q_num == 7:
        return f"Imagine a high-priority {career_title} project deadline is 48 hours away, but a critical unexpected bug threatens release. Walk me through your step-by-step resolution triage strategy."

    else:
        return f"Finally, if a major production crash occurs right after a release in a {career_title} system, what is your immediate incident response plan from discovery to post-mortem?"


# ============================================================

# 4-METRIC ANSWER EVALUATOR ALGORITHM
# ============================================================

def evaluate_interview_answer(career, question_text: str, stage: str, user_answer: str) -> Dict[str, Any]:
    """
    Evaluate user's answer dynamically across 4 core metrics:
    1. Technical Accuracy (0-100)
    2. Communication Clarity (0-100)
    3. Confidence & Tone (0-100)
    4. STAR Structure / Relevance (0-100)
    """
    clean_answer = (user_answer or "").strip()
    words = clean_answer.split()
    word_count = len(words)

    if word_count < 5:
        return {
            "accuracy_score": 25.0,
            "clarity_score": 30.0,
            "confidence_score": 20.0,
            "structure_score": 20.0,
            "overall_question_score": 23.8,
            "feedback_notes": "Your answer was too brief. Try to elaborate on your reasoning, give specific examples, and explain your strategy in 3-5 complete sentences.",
            "ideal_answer": get_model_ideal_answer(career, stage, question_text)
        }

    # 1. Technical Accuracy & Domain Knowledge
    skills_keywords = [s.strip().lower() for s in (career.skills or "").split(",") if s.strip()]
    domain_keywords = [
        career.title.lower(), career.category.lower(), "system", "process", "data", "quality", "strategy",
        "solution", "tool", "framework", "analysis", "workflow", "code", "development", "project", "kaam", "tajruba", "mushkil", "hal"
    ]
    all_target_keywords = set(skills_keywords + domain_keywords)
    
    found_keywords = [kw for kw in all_target_keywords if kw in clean_answer.lower()]
    base_accuracy = min(100.0, 50.0 + (len(found_keywords) * 12.0) + (word_count * 0.4))

    # 2. Communication Clarity
    fillers = ["um", "uh", "like", "you know", "i guess", "stuff", "basically", "whatever"]
    filler_count = sum(clean_answer.lower().count(f) for f in fillers)
    clarity_deduction = filler_count * 8.0
    
    length_score = 100.0 if 30 <= word_count <= 180 else (75.0 if word_count < 30 else 85.0)
    base_clarity = max(35.0, min(100.0, length_score - clarity_deduction))

    # 3. Confidence & Tone (Supports English & Roman Urdu active verbs)
    strong_words = [
        "achieved", "delivered", "implemented", "solved", "spearheaded", "ensured", "optimized", "managed", "designed",
        "built", "successfully", "confident", "analyzed", "resolved", "main", "hoon", "karta", "karti", "karte", "karna",
        "banaya", "samjha", "seekha", "koshish", "tajruba", "achha", "boht", "team", "manage"
    ]
    weak_words = ["maybe", "i don't know", "not sure", "possibly", "kind of", "sort of", "pata nahi"]
    
    strong_hits = sum(1 for w in strong_words if w in clean_answer.lower())
    weak_hits = sum(1 for w in weak_words if w in clean_answer.lower())
    
    base_confidence = min(100.0, max(40.0, 60.0 + (strong_hits * 8.0) - (weak_hits * 15.0)))

    # 4. STAR Structure & Relevance (Supports English & Roman Urdu structural connectors)
    star_markers = [
        "situation", "task", "action", "result", "outcome", "challenge", "solution", "first", "then", "finally",
        "consequently", "because", "impact", "pehle", "phir", "mushkil", "waja", "sath", "process"
    ]
    star_hits = sum(1 for sm in star_markers if sm in clean_answer.lower())
    base_structure = min(100.0, max(45.0, 50.0 + (star_hits * 10.0)))


    # Compute Weighted Overall Score for Question
    overall_question_score = round(
        (base_accuracy * 0.35) +
        (base_clarity * 0.25) +
        (base_confidence * 0.20) +
        (base_structure * 0.20),
        1
    )

    # Generate Personalized Feedback
    feedback_parts = []
    if base_accuracy >= 75:
        feedback_parts.append("Great technical relevance and domain terminology.")
    else:
        feedback_parts.append(f"Consider referencing specific {career.title} tools ({', '.join(skills_keywords[:3])}) to enhance technical authority.")

    if base_clarity >= 80:
        feedback_parts.append("Your response is articulate and well-paced.")
    elif filler_count > 0:
        feedback_parts.append("Try reducing filler words to keep your presentation crisp.")

    if base_confidence >= 80:
        feedback_parts.append("Strong, assertive tone.")

    if base_structure >= 75:
        feedback_parts.append("Good structural flow (Situation → Action → Result).")
    else:
        feedback_parts.append("Structure your answer using the STAR method: state the Situation, your specific Action, and the quantifiable Result.")

    feedback_notes = " ".join(feedback_parts)
    ideal_answer = get_model_ideal_answer(career, stage, question_text)

    return {
        "accuracy_score": round(base_accuracy, 1),
        "clarity_score": round(base_clarity, 1),
        "confidence_score": round(base_confidence, 1),
        "structure_score": round(base_structure, 1),
        "overall_question_score": overall_question_score,
        "feedback_notes": feedback_notes,
        "ideal_answer": ideal_answer
    }


def get_model_ideal_answer(career, stage: str, question_text: str, question_number: int = None) -> str:
    """Return exemplary model answer specific to each question for benchmark comparison."""
    title = career.title
    category = career.category or "this field"
    skills = career.skills or "industry tools and best practices"
    q_lower = (question_text or "").lower()

    if question_number == 1 or "introduce yourself" in q_lower or "passionate" in q_lower:
        return f"\"I am deeply passionate about a career as a {title} because it combines innovative problem-solving with real-world impact in {category}. Over the past year, I have built solid hands-on experience in {skills}. My key strength lies in adapting quickly to new technical challenges and delivering clean, reliable work that aligns with team goals.\""

    elif question_number == 2 or "challenging situation" in q_lower or "obstacles" in q_lower:
        return f"\"During a recent project, unexpected technical bugs and tight timelines threatened our milestones. I organized the workload by breaking complex tasks into smaller sub-modules, prioritized critical paths, and maintained daily status updates with my team. As a result, we identified the root cause, implemented automated tests, and successfully delivered the project on schedule.\""

    elif question_number == 3 or "conflicting deadlines" in q_lower or "opinion" in q_lower:
        return f"\"When priorities shift or architectural disagreements arise, I focus on data-driven evaluation and transparent dialogue. I evaluate trade-offs with my team, align on the primary business objective, and execute the agreed strategy with full commitment.\""

    elif question_number == 4 or "best practices" in q_lower or "architecture" in q_lower:
        return f"\"When applying core skills like {skills} in a {title} role, I strictly follow industry best practices: writing modular and self-documenting code/workflows, conducting thorough peer reviews, establishing robust testing pipelines, and maintaining clear documentation so systems remain scalable and easy to maintain.\""

    elif question_number == 5 or "performance optimization" in q_lower or "review process" in q_lower:
        return f"\"In performance optimization and debugging, I use profiling tools to isolate bottlenecks, enforce automated unit testing, and optimize database/query structures. In code reviews, I focus on maintainability, security standards, and minimizing technical debt.\""

    elif question_number == 6 or "non-technical" in q_lower or "explain" in q_lower:
        return f"\"When communicating complex concepts to non-technical stakeholders, I avoid heavy jargon. Instead, I use relatable real-world analogies, visual flowcharts, and focus on business outcomes—explaining what the solution achieves, why it matters, and how it delivers quantifiable value to the organization.\""

    elif question_number == 7 or "48 hours" in q_lower or "deadline" in q_lower:
        return f"\"In a high-pressure 48-hour delivery scenario, my immediate action is to triage: first, conduct a rapid root-cause analysis of the blocking issue, communicate transparently with project leads, agree on MVP priorities, and execute a focused, step-by-step resolution strategy to deliver the solution reliably without sacrificing quality.\""

    elif question_number == 8 or "production" in q_lower or "failure" in q_lower or "upskill" in q_lower:
        return f"\"When facing production emergencies or new tool requirements, I follow a 3-step protocol: isolate the incident to prevent escalation, implement a rapid rollback or fix, and conduct a transparent post-mortem to fortify system stability for future releases.\""

    # Fallback per stage
    if stage == "HR":
        return f"\"I combine domain knowledge in {category} with technical proficiency in {skills} to drive team success and deliver measurable outcomes.\""
    elif stage == "TECHNICAL":
        return f"\"I adhere to industry best practices in {skills}, ensuring clear architecture, thorough verification, and effective technical communication.\""
    else:
        return f"\"Under tight deadlines, I prioritize transparent communication, root-cause triage, and step-by-step execution to achieve goal success.\""




# ============================================================
# FINAL REPORT SYNTHESIZER
# ============================================================

def generate_final_interview_report(session):
    """
    Calculate session averages across all responses and generate comprehensive final report.
    """
    responses = session.responses.all()
    if not responses.exists():
        return

    count = responses.count()
    avg_overall = sum(r.overall_question_score for r in responses) / count
    avg_accuracy = sum(r.accuracy_score for r in responses) / count
    avg_clarity = sum(r.clarity_score for r in responses) / count
    avg_confidence = sum(r.confidence_score for r in responses) / count
    avg_star = sum(r.structure_score for r in responses) / count

    session.overall_score = round(avg_overall, 1)
    session.technical_score = round(avg_accuracy, 1)
    session.clarity_score = round(avg_clarity, 1)
    session.confidence_score = round(avg_confidence, 1)
    session.star_score = round(avg_star, 1)

    # Extract Strengths & Growth Areas
    strengths = []
    improvements = []

    if avg_accuracy >= 75:
        strengths.append(f"Strong technical command of {session.career.title} concepts and tools.")
    else:
        improvements.append(f"Deepen your familiarity with core technical keywords for {session.career.title}.")

    if avg_clarity >= 75:
        strengths.append("Articulate communication style with clear sentence structure.")
    else:
        improvements.append("Practice concise delivery and reduce hesitation filler words.")

    if avg_confidence >= 75:
        strengths.append("Assertive, confident professional tone.")
    else:
        improvements.append("Use more active action verbs (e.g., 'I executed', 'I resolved').")

    if avg_star >= 75:
        strengths.append("Excellent structured answer delivery using the STAR framework.")
    else:
        improvements.append("Adopt the STAR framework (Situation, Task, Action, Result) to format your responses.")

    session.strengths = strengths if strengths else ["Completed full multi-stage AI interview."]
    session.improvements = improvements if improvements else ["Keep practicing to maintain top interview readiness."]

    if avg_overall >= 80:
        session.summary_notes = f"Outstanding performance! You demonstrated strong interview readiness for {session.career.title} role."
    elif avg_overall >= 60:
        session.summary_notes = f"Good overall performance! You have a solid foundation for {session.career.title}. Review the feedback to polish your delivery."
    else:
        session.summary_notes = f"Fair attempt! Focus on building your technical terminology and practicing structured STAR responses for {session.career.title}."

    session.status = "completed"
    session.save()
