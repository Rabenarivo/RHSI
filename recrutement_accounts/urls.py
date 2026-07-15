from django.urls import path
from . import views

app_name = 'recrutement_accounts'

urlpatterns = [
    path('register/', views.register, name='register'),
]
