from django.urls import path

from .feedback import submit_career_feedback
from .pdf_generator import download_report
from .views import recommend_careers


urlpatterns = [
    path(
        "careers/<int:result_id>/",
        recommend_careers,
        name="recommend_careers",
    ),
    path(
        "download-report/<int:result_id>/",
        download_report,
        name="download_report",
    ),
    path(
        "feedback/<int:result_id>/",
        submit_career_feedback,
        name="submit_career_feedback",
    ),
]