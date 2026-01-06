from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', RedirectView.as_view(pattern_name='weeks:weeks_list', permanent=False)), 
    path('weeks/', include('weeks.urls')),
    path('members/', include('members.urls')),
    path('teams/', include('teams.urls')),
]