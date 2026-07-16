from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('recrutement_accounts.urls')),
    path('jobs/', include('recrutement_jobs.urls')),
]
