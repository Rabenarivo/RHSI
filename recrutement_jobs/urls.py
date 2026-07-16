from django.urls import path
from . import views

app_name = 'recrutement_jobs'

urlpatterns = [
    path('create_job_offer/', views.create_job_offer, name='create_job_offer'),
]