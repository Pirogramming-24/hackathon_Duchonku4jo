from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponseRedirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', HttpResponseRedirect('/teams/1/')),  # 🔥 reverse 제거
    path('teams/', include('teams.urls')),
]
