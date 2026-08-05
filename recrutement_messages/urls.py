from django.urls import path
from . import views

app_name = 'recrutement_messages'

urlpatterns = [
    path('inbox/', views.inbox, name='inbox'),
    path('sent/', views.sent_messages, name='sent_messages'),
    path('compose/', views.compose, name='compose'),
    path('read/<int:message_id>/', views.read_message, name='read_message'),
]
