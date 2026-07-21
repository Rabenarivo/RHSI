from django.urls import path
from . import views

app_name = 'recrutement_jobs'

urlpatterns = [
    path('create_job_offer/', views.create_job_offer, name='create_job_offer'),
    path('list_job_offer/', views.list_job_offer, name='list_job_offer'),
    path('<int:job_offer_id>/application_postuler/', views.application_postuler, name='application_postuler'),
    path('application_filter/', views.get_applictaion_filter, name='application_filter'),
]