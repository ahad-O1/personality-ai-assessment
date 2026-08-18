from django.db import models
from django.conf import settings
from django.utils import timezone

from assessment.models import AssessmentResult


class Career(models.Model):
    CATEGORY_CHOICES = [
        ("Technology", "Technology"),
        ("Medical", "Medical"),
        ("Education", "Education"),
        ("Business", "Business"),
        ("Engineering", "Engineering"),
        ("Creative", "Creative"),
        ("Public Service", "Public Service"),
    ]

    objects = models.Manager()

    title = models.CharField(max_length=100)
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        default="Technology"
    )

    description = models.TextField()
    required_traits = models.CharField(max_length=200)
    skills = models.TextField()

    min_openness = models.IntegerField(default=0)
    min_conscientiousness = models.IntegerField(default=0)
    min_extraversion = models.IntegerField(default=0)
    min_agreeableness = models.IntegerField(default=0)
    max_neuroticism = models.IntegerField(default=100)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

        
class CareerFeedback(models.Model):

    RATING_CHOICES = [
        (1, "Very Poor"),
        (2, "Poor"),
        (3, "Average"),
        (4, "Good"),
        (5, "Excellent"),
    ]

    objects = models.Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="career_feedbacks"
    )

    assessment_result = models.ForeignKey(
        AssessmentResult,
        on_delete=models.CASCADE,
        related_name="career_feedbacks"
    )

    career = models.ForeignKey(
        "Career",
        on_delete=models.CASCADE,
        related_name="feedbacks"
    )

    rating = models.PositiveSmallIntegerField(
        choices=RATING_CHOICES
    )

    is_relevant = models.BooleanField(
        default=True,
        help_text="User considers this career suitable."
    )

    comments = models.TextField(
        blank=True
    )
    used_for_training = models.BooleanField(
    default=False,
    help_text="Shows whether this feedback has already been used for model retraining."
)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

        constraints = [
            models.UniqueConstraint(
                fields=["user", "assessment_result", "career"],
                name="unique_user_result_career_feedback"
            )
        ]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.career.title} - "
            f"{self.rating}/5"
        )        

class AIModelStatus(models.Model):
    """
    Stores the current AI model information.
    Only one record should exist.
    """

    objects = models.Manager()

    model_version = models.CharField(
        max_length=20,
        default="1.0"
    )

    current_accuracy = models.FloatField(
        default=0
    )

    previous_accuracy = models.FloatField(
        default=0
    )

    feedback_since_last_training = models.PositiveIntegerField(
        default=0
    )

    last_retrained = models.DateTimeField(
        null=True,
        blank=True
    )

    retraining_running = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"Career Model v{self.model_version}"


class UserRoadmapProgress(models.Model):
    """Tracks completed learning roadmap steps per user and career."""

    objects = models.Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="roadmap_progresses"
    )
    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="user_progresses"
    )
    step_index = models.PositiveIntegerField()
    completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["step_index"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "career", "step_index"],
                name="unique_user_career_step"
            )
        ]

    def __str__(self):
        status = "Done" if self.completed else "Pending"
        return f"{self.user.username} - {self.career.title} Step {self.step_index}: {status}"


class UserCareerGoal(models.Model):
    """Tracks active target career chosen by a user along with goal settings and streak."""
    objects = models.Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="career_goals"
    )
    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="user_goals"
    )
    is_active = models.BooleanField(default=True)
    daily_reminder_enabled = models.BooleanField(default=True)
    reminder_time = models.CharField(max_length=10, default="20:00")
    streak_count = models.PositiveIntegerField(default=0)
    last_active_date = models.DateField(null=True, blank=True)
    target_completion_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        active_status = "Active" if self.is_active else "Inactive"
        return f"{self.user.username} - Goal: {self.career.title} ({active_status})"


class UserDailyLog(models.Model):
    """Stores daily progress log entry for a user's active career goal."""
    objects = models.Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="daily_logs"
    )
    career_goal = models.ForeignKey(
        UserCareerGoal,
        on_delete=models.CASCADE,
        related_name="daily_logs"
    )
    date = models.DateField(default=timezone.now)
    study_duration_minutes = models.PositiveIntegerField(default=30)
    notes = models.TextField(blank=True, help_text="Notes/reflections on what was learned today")
    completed = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "career_goal", "date"],
                name="unique_user_goal_daily_log"
            )
        ]

    def __str__(self):
        return f"{self.user.username} - Log {self.date}: {self.study_duration_minutes}m"


class UserInterviewSession(models.Model):
    """Stores an interactive AI Mock Interview session for a career."""
    STATUS_CHOICES = [
        ("in_progress", "In Progress"),
        ("completed", "Completed"),
    ]

    objects = models.Manager()

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="interview_sessions"
    )
    career = models.ForeignKey(
        Career,
        on_delete=models.CASCADE,
        related_name="interview_sessions"
    )
    assessment_result = models.ForeignKey(
        AssessmentResult,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="interview_sessions"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="in_progress"
    )
    total_questions = models.PositiveIntegerField(default=5)
    current_question_index = models.PositiveIntegerField(default=1)

    overall_score = models.FloatField(default=0.0)
    technical_score = models.FloatField(default=0.0)
    clarity_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    star_score = models.FloatField(default=0.0)

    strengths = models.JSONField(default=list, blank=True)
    improvements = models.JSONField(default=list, blank=True)
    summary_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - Interview: {self.career.title} ({self.status})"


class UserInterviewResponse(models.Model):
    """Stores individual question response and multi-metric AI evaluation."""
    STAGE_CHOICES = [
        ("HR", "HR & Behavioral"),
        ("TECHNICAL", "Technical & Concepts"),
        ("SITUATIONAL", "Situational Scenario"),
    ]

    objects = models.Manager()

    session = models.ForeignKey(
        UserInterviewSession,
        on_delete=models.CASCADE,
        related_name="responses"
    )
    question_number = models.PositiveIntegerField()
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default="HR")
    question_text = models.TextField()
    user_answer = models.TextField(blank=True)

    accuracy_score = models.FloatField(default=0.0)
    clarity_score = models.FloatField(default=0.0)
    confidence_score = models.FloatField(default=0.0)
    structure_score = models.FloatField(default=0.0)
    overall_question_score = models.FloatField(default=0.0)

    feedback_notes = models.TextField(blank=True)
    ideal_answer = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["question_number"]
        constraints = [
            models.UniqueConstraint(
                fields=["session", "question_number"],
                name="unique_session_question_number"
            )
        ]

    def __str__(self):
        return f"Session #{self.session.id} Q{self.question_number}: {self.stage}"


        