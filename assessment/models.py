from django.db import models
from django.contrib.auth.models import User


class Question(models.Model):

    TRAIT_CHOICES = [
        ('O', 'Openness'),
        ('C', 'Conscientiousness'),
        ('E', 'Extraversion'),
        ('A', 'Agreeableness'),
        ('N', 'Neuroticism'),
    ]

    question_text = models.TextField()
    question_text_ur = models.TextField(blank=True, null=True)
    question_text_roman = models.TextField(blank=True, null=True)

    trait = models.CharField(
        max_length=1,
        choices=TRAIT_CHOICES
    )

    facet = models.CharField(
        max_length=100,
        blank=True,
        null=True
    )

    weight = models.IntegerField(default=1)

    reverse_scoring = models.BooleanField(default=False)

    difficulty = models.IntegerField(default=3)

    discrimination = models.FloatField(default=1.0)

    times_used = models.IntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question_text


class AssessmentSession(models.Model):

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    started_at = models.DateTimeField(auto_now_add=True)

    completed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} Session"


class UserResponse(models.Model):

    session = models.ForeignKey(
        AssessmentSession,
        on_delete=models.CASCADE
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE
    )

    answer_value = models.IntegerField()

    answered_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.user.username} - {self.question.id}"


class AssessmentResult(models.Model):

    session = models.OneToOneField(
        AssessmentSession,
        on_delete=models.CASCADE
    )

    openness = models.FloatField(default=0)
    conscientiousness = models.FloatField(default=0)
    extraversion = models.FloatField(default=0)
    agreeableness = models.FloatField(default=0)
    neuroticism = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.session.user.username} Result"