from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", include("home.urls")),

    path("accounts/", include("accounts.urls")),
    path("assessment/", include("assessment.urls")),
    path("recommendations/", include("recommendations.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("chatbot/", include("chatbot.urls")),
]