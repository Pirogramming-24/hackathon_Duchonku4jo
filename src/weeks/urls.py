from django.urls import path
from .import views

app_name ='weeks'

urlpatterns = [
    path("", views.weeks_list, name="weeks_list"),
    path("create/", views.week_create, name="week_create"),
    path("<int:pk>/delete/", views.week_delete, name="week_delete"),
]