from django.urls import path
from .import views

app_name ='weeks'

urlpatterns = [
    path('', views.week_list, name='week_list'),
    path('create/', views.week_create, name='week_create'),
    path('<int:week_id>/delete/', views.week_delete, name='week_delete'),
]