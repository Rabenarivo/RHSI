from django.urls import path
from . import views

app_name = 'recrutement_payroll'

urlpatterns = [
    path('configuration/', views.edit_configuration, name='edit_configuration'),
    path('pointage/', views.pointage_action, name='pointage_action'),
    path('admin-list/', views.admin_list_payroll, name='admin_list_payroll'),
    path('generate/', views.generate_payroll, name='generate_payroll'),
    path('my-payslips/', views.employee_list_payroll, name='employee_list_payroll'),
    path('slip/<int:slip_id>/', views.payslip_detail, name='payslip_detail'),
]
