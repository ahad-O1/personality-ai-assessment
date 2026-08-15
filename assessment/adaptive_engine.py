"""
Adaptive Question Engine v3
---------------------------

This module controls the AI-based adaptive assessment flow.

Main idea:
- User does NOT answer all 200 questions.
- System checks user's answers after every question.
- It calculates confidence for each Big Five trait.
- It selects the next best question from the weakest trait/facet.
- Assessment stops automatically when confidence is high enough.

This is inspired by:
- Computerized Adaptive Testing (CAT)
- Item Response Theory concepts
- Trait confidence estimation
"""

from collections import defaultdict
from statistics import pstdev

from .models import Question, UserResponse


# ----------------------------
# Global Adaptive Settings
# ----------------------------

TRAITS = ["O", "C", "E", "A", "N"]

MIN_QUESTIONS = 15                  # Minimum baseline questions for statistical validity
MAX_QUESTIONS = 200                 # Full question pool (stopping is purely AI confidence-driven)

OVERALL_CONFIDENCE_THRESHOLD = 80   # AI overall confidence threshold
TRAIT_CONFIDENCE_THRESHOLD = 75     # AI trait-level confidence threshold

MIN_QUESTIONS_PER_TRAIT = 3


# ----------------------------
# Reverse Scoring
# ----------------------------

def get_adjusted_answer(question, answer_value):
    """
    Converts reverse-scored answers.

    Normal question:
        1 stays 1, 5 stays 5

    Reverse question:
        1 becomes 5
        2 becomes 4
        3 stays 3
        4 becomes 2
        5 becomes 1
    """

    if question.reverse_scoring:
        return 6 - answer_value

    return answer_value


# ----------------------------
# Session Score Collection
# ----------------------------

def get_session_scores(session):
    """
    Collect all user responses for current session.

    Returns:
        scores:
            {
                "O": [4, 5, 3],
                "C": [2, 4],
                ...
            }

        facet_counts:
            {
                ("O", "Imagination"): 2,
                ("C", "Orderliness"): 1
            }
    """

    scores = {trait: [] for trait in TRAITS}
    facet_counts = defaultdict(int)

    responses = (
        UserResponse.objects
        .filter(session=session)
        .select_related("question")
    )

    for response in responses:
        question = response.question

        adjusted_answer = get_adjusted_answer(
            question,
            response.answer_value
        )

        scores[question.trait].append(adjusted_answer)

        if question.facet:
            facet_counts[(question.trait, question.facet)] += 1

    return scores, facet_counts


# ----------------------------
# Facet Coverage
# ----------------------------

def get_trait_facets(trait):
    """
    Returns all available facets for a trait.

    Example:
        Trait O may have:
        - Imagination
        - Artistic Interests
        - Emotionality
        - Adventurousness
        - Intellect
        - Liberalism
    """

    return list(
        Question.objects.filter(
            is_active=True,
            trait=trait
        )
        .exclude(facet__isnull=True)
        .exclude(facet="")
        .values_list("facet", flat=True)
        .distinct()
    )


def calculate_facet_coverage(trait, facet_counts):
    """
    Calculates how many facets of a trait have been covered.

    Example:
        Openness has 6 facets.
        User answered questions from 3 facets.

        Coverage = 3 / 6 * 100 = 50%
    """

    facets = get_trait_facets(trait)

    if not facets:
        return 100

    covered = 0

    for facet in facets:
        if facet_counts.get((trait, facet), 0) > 0:
            covered += 1

    return round((covered / len(facets)) * 100, 2)


# ----------------------------
# Confidence Calculation
# ----------------------------

def calculate_trait_confidence(trait, values, facet_counts):
    """
    Calculates confidence for a single trait smoothly without erratic drops.

    Factors:
    1. Evidence Score (up to 40 pts):
       Grows steadily with each answered question. 5-6 questions per trait = max points.

    2. Consistency Score (up to 25 pts):
       Gentle penalty for standard deviation so normal human answer variation
       doesn't plummet the score.

    3. Stability Score (up to 20 pts):
       Measures overall deviation from average across all answered trait questions
       rather than volatile last-two-answers comparison.

    4. Facet Coverage Score (up to 15 pts):
       Bonus for answering questions across different facets.
    """

    answered = len(values)

    if answered == 0:
        return 0.0

    # 1. Evidence score (up to 40 pts, full evidence at 6 questions)
    evidence_score = min((answered / 6) * 40, 40)

    # 2. Consistency score (up to 25 pts, gentle scale for SD)
    if answered >= 2:
        standard_deviation = pstdev(values)
        consistency_score = max(5, 25 - (standard_deviation * 8))
    else:
        consistency_score = 15

    # 3. Stability score (up to 20 pts based on overall deviation from trait mean)
    if answered >= 3:
        average = sum(values) / answered
        avg_deviation = sum(abs(v - average) for v in values) / answered
        stability_score = max(5, 20 - (avg_deviation * 6))
    else:
        stability_score = 12

    # 4. Facet coverage score (up to 15 pts)
    facet_coverage = calculate_facet_coverage(trait, facet_counts)
    coverage_score = (facet_coverage / 100) * 15

    total_confidence = (
        evidence_score
        + consistency_score
        + stability_score
        + coverage_score
    )

    return round(min(total_confidence, 100), 2)


def calculate_confidence(scores, facet_counts):
    """
    Calculates confidence for all OCEAN traits.

    Returns:
        overall_confidence
        trait_confidences
    """

    trait_confidences = {}

    for trait in TRAITS:
        trait_confidences[trait] = calculate_trait_confidence(
            trait,
            scores[trait],
            facet_counts
        )

    overall_confidence = round(
        sum(trait_confidences.values()) / len(TRAITS),
        2
    )

    return overall_confidence, trait_confidences


# ----------------------------
# Trait Selection
# ----------------------------

def get_lowest_confidence_trait(trait_confidences, scores):
    """
    Selects the trait that needs more questions.

    Priority:
    1. Traits with fewer than minimum required questions.
    2. Otherwise, trait with lowest confidence.
    """

    under_tested_traits = [
        trait for trait in TRAITS
        if len(scores[trait]) < MIN_QUESTIONS_PER_TRAIT
    ]

    if under_tested_traits:
        return min(
            under_tested_traits,
            key=lambda trait: len(scores[trait])
        )

    return min(
        trait_confidences,
        key=trait_confidences.get
    )


# ----------------------------
# Question Information Score
# ----------------------------

def get_question_information_score(question, facet_counts, answered_count):
    """
    Scores how useful a question is.

    Higher score means better question.

    Factors:
    - discrimination: more important questions get higher score.
    - facet usage: less used facets get priority.
    - times_used: overused questions get lower score.
    - difficulty: medium difficulty is preferred early.
    - phase score: difficulty changes based on assessment stage.
    """

    facet_usage = facet_counts.get(
        (question.trait, question.facet),
        0
    )

    discrimination_score = question.discrimination * 25

    facet_score = max(
        0,
        20 - (facet_usage * 5)
    )

    usage_score = max(
        0,
        15 - (question.times_used * 0.3)
    )

    difficulty_score = max(
        0,
        10 - abs(question.difficulty - 3) * 3
    )

    # Adaptive difficulty phase
    if answered_count < 15:
        phase_score = 10 if question.difficulty <= 3 else 3
    elif answered_count < 35:
        phase_score = 10
    else:
        phase_score = 10 if question.difficulty >= 3 else 5

    return (
        discrimination_score
        + facet_score
        + usage_score
        + difficulty_score
        + phase_score
    )


def select_best_question(candidate_questions, facet_counts, answered_count):
    """
    Selects the best question from candidate questions
    using information score.
    """

    best_question = None
    best_score = -999999

    for question in candidate_questions:
        score = get_question_information_score(
            question,
            facet_counts,
            answered_count
        )

        if score > best_score:
            best_score = score
            best_question = question

    return best_question


# ----------------------------
# Stopping Rule
# ----------------------------

def should_stop_assessment(
    answered_count,
    scores,
    overall_confidence,
    trait_confidences
):
    """
    Decides whether assessment should stop.

    Stopping is driven PURELY by AI confidence:
    - Minimum 15 questions answered (for basic statistical validity).
    - Every trait has answered at least 3 questions.
    - AI overall confidence meets the target threshold (80%).
    - Each individual trait confidence meets target threshold (75%).
    """

    if answered_count < MIN_QUESTIONS:
        return False

    all_traits_have_min_questions = all(
        len(scores[trait]) >= MIN_QUESTIONS_PER_TRAIT
        for trait in TRAITS
    )

    all_traits_confident = all(
        confidence >= TRAIT_CONFIDENCE_THRESHOLD
        for confidence in trait_confidences.values()
    )

    # Pure AI Confidence-driven stopping condition
    if (
        overall_confidence >= OVERALL_CONFIDENCE_THRESHOLD
        and all_traits_confident
        and all_traits_have_min_questions
    ):
        return True

    return False


# ----------------------------
# Main Adaptive AI Function
# ----------------------------

def select_next_question(session):
    """
    Main AI function.

    This function:
    1. Reads user answers.
    2. Calculates trait confidence.
    3. Checks if assessment should stop.
    4. Finds weakest trait.
    5. Selects the most informative next question.
    """

    scores, facet_counts = get_session_scores(session)

    overall_confidence, trait_confidences = calculate_confidence(
        scores,
        facet_counts
    )

    answered_ids = list(
        UserResponse.objects.filter(session=session)
        .values_list("question_id", flat=True)
    )

    answered_count = len(answered_ids)

    if should_stop_assessment(
        answered_count,
        scores,
        overall_confidence,
        trait_confidences
    ):
        return None, overall_confidence, trait_confidences

    target_trait = get_lowest_confidence_trait(
        trait_confidences,
        scores
    )

    candidate_questions = (
        Question.objects
        .filter(
            is_active=True,
            trait=target_trait
        )
        .exclude(id__in=answered_ids)
    )

    # Backup if no question remains in selected trait
    if not candidate_questions.exists():
        candidate_questions = (
            Question.objects
            .filter(is_active=True)
            .exclude(id__in=answered_ids)
        )

    best_question = select_best_question(
        candidate_questions,
        facet_counts,
        answered_count
    )

    return best_question, overall_confidence, trait_confidences


# ----------------------------
# Final OCEAN Score
# ----------------------------

def average_score(values):
    """
    Converts Likert average into percentage.

    Likert scale:
        1 to 5

    Percentage:
        average * 20
    """

    if not values:
        return 0

    return round((sum(values) / len(values)) * 20, 2)