from django.urls import path
from . import views

app_name = 'recrutement_payroll'

urlpatterns = [
    path('configuration/', views.edit_configuration, name='edit_configuration'),
    path('pointage/', views.pointage_action, name='pointage_action'),
]
