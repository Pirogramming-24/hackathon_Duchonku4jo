# members/urls.py
from django.urls import path
from . import views

app_name = 'members'

urlpatterns = [
    path('', views.member_list, name='member_list'),           # GET /members/
    path('create/', views.member_create, name='member_create'),# POST /members/create/
    path('<int:member_id>/delete/', views.member_delete, name='member_delete'),
]
