from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'), 
    path('generate/', views.generate_teams, name='generate_teams'), # 새로고침 시마다 알고리즘 재실행 [cite: 133]
    path('save/', views.save_teams, name='save_teams'),            # DB 확정 저장 [cite: 134]
]