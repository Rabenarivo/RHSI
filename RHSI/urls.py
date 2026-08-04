from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('recrutement_accounts.urls')),
    path('jobs/', include('recrutement_jobs.urls')),
    path('interviews/', include('recrutement_interviews.urls')),
    path('payroll/', include('recrutement_payroll.urls')),
]
