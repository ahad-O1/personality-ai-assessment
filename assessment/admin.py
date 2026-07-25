from django.contrib import admin
from .models import Question, AssessmentSession, UserResponse, AssessmentResult

admin.site.register(Question)
admin.site.register(AssessmentSession)
admin.site.register(UserResponse)
admin.site.register(AssessmentResult)