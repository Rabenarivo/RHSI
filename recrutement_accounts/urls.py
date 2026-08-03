from django.urls import path
from . import views

app_name = 'recrutement_accounts'

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('assign-manager/', views.assign_manager, name='assign_manager'),
    path('manager-emp/', views.get_manager_emp, name='get_manager_emp'),
    path('demande-conge/', views.create_conges, name='create_conges'),
    path('leave/<int:leave_id>/<str:status>/', views.change_leave_status, name='change_leave_status'),
]
