from django.contrib import admin
from .models import AccountType, Account, Candidate

admin.site.register(AccountType)
admin.site.register(Account)
admin.site.register(Candidate)
