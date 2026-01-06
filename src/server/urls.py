# src/server/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect # redirect는 callable을 반환하는 헬퍼 함수입니다.

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # 1. 람다(lambda)를 사용하는 올바른 방법 (가장 간단)
    path('', lambda r: redirect('teams:team_home', week_id=1)),
    
    # 만약 위 방법이 불안하다면 아래처럼 직접 경로를 적어줘도 됩니다 (함수 아님, 단순 리다이렉트 전용)
    # from django.views.generic import RedirectView
    # path('', RedirectView.as_view(url='/teams/home/1/')),

    path('teams/', include('teams.urls')),
]