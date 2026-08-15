from django.db import models
from django.conf import settings
from django.db import models

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