from django.contrib import admin
from .models import AccountType, Account, Candidate, Employee

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Candidate)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'manager', 'account')
    list_filter = ('manager',)
    search_fields = ('first_name', 'last_name')
    
admin.site.register(Employee, EmployeeAdmin)
