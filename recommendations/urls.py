from django.urls import path

from .feedback import submit_career_feedback
from .pdf_generator import download_report
from .interview_views import (
    start_interview_session,
    submit_interview_answer,
    interview_summary_report,
)
from .views import (
    recommend_careers,
    toggle_roadmap_step,
    compare_careers,
    select_career_goal,
    career_tracker_dashboard,
    log_daily_progress,
    update_reminder_settings,
    check_daily_reminder,
)


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
    path(
        "toggle-roadmap-step/",
        toggle_roadmap_step,
        name="toggle_roadmap_step",
    ),
    path(
        "compare/<int:result_id>/",
        compare_careers,
        name="compare_careers",
    ),
    path(
        "select-goal/<int:career_id>/",
        select_career_goal,
        name="select_career_goal",
    ),
    path(
        "tracker/",
        career_tracker_dashboard,
        name="career_tracker_dashboard",
    ),
    path(
        "log-daily-progress/",
        log_daily_progress,
        name="log_daily_progress",
    ),
    path(
        "update-reminder/",
        update_reminder_settings,
        name="update_reminder_settings",
    ),
    path(
        "api/check-reminder/",
        check_daily_reminder,
        name="check_daily_reminder",
    ),
    path(
        "interview/start/<int:career_id>/",
        start_interview_session,
        name="start_interview_session",
    ),
    path(
        "interview/submit/<int:session_id>/",
        submit_interview_answer,
        name="submit_interview_answer",
    ),
    path(
        "interview/report/<int:session_id>/",
        interview_summary_report,
        name="interview_summary_report",
    ),
]