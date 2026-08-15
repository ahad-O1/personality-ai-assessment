from django.urls import path
from . import views

app_name = "assessment"

urlpatterns = [
    path("start/", views.start_assessment, name="start_assessment"),
    path("questions/<int:session_id>/", views.question_page, name="question_page"),
]
