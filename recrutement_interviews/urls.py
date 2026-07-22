from django.urls import path
from . import views

app_name = 'recrutement_interviews'

urlpatterns = [
    path('application_filter/', views.list_application_filter, name='application_filter'),
    path('create_interview/<int:application_id>/', views.create_Interview, name='create_interview'),
]