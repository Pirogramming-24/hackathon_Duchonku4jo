from django.urls import path
from . import views

app_name = "teams"

urlpatterns = [
    path("<int:week_id>/", views.team_home, name="team_home"),
    path("<int:week_id>/scores/", views.score_input, name="score_input"),
    path("<int:week_id>/preview/", views.team_preview, name="team_preview"),
    path("<int:week_id>/save/", views.team_save, name="team_save"),
]
