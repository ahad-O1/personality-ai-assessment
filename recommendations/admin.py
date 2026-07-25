from django.contrib import admin

from .models import Career, CareerFeedback, AIModelStatus

@admin.register(Career)
class CareerAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "category",
        "is_active",
    )

    list_filter = (
        "category",
        "is_active",
    )

    search_fields = (
        "title",
        "description",
        "skills",
    )


@admin.register(CareerFeedback)
class CareerFeedbackAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "career",
        "rating",
        "is_relevant",
        "used_for_training",
        "created_at",
    )

    list_filter = (
        "rating",
        "is_relevant",
        "career__category",
        "used_for_training",
        "created_at",
    )

    search_fields = (
        "user__username",
        "career__title",
        "comments",
    )

    readonly_fields = (
        "created_at",
    )

@admin.register(AIModelStatus)
class AIModelStatusAdmin(admin.ModelAdmin):
    list_display = (
        "model_version",
        "current_accuracy",
        "previous_accuracy",
        "feedback_since_last_training",
        "last_retrained",
        "retraining_running",
    )

    readonly_fields = (
        "model_version",
        "current_accuracy",
        "previous_accuracy",
        "feedback_since_last_training",
        "last_retrained",
        "retraining_running",
    )

    def has_add_permission(self, request):
        """
        Only one AIModelStatus record should exist.
        """
        return not AIModelStatus.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """
        Prevent accidental deletion of the model status record.
        """
        return False    