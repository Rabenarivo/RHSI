from django.db import models

class AccountType(models.Model):
    name = models.CharField(max_length=50, help_text="admin, recruteur, candidat")

    def __str__(self):
        return self.name

class Account(models.Model):
    account_type = models.ForeignKey(AccountType, on_delete=models.CASCADE, related_name='accounts')
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    entreprise = models.CharField(max_length=100, null=True, blank=True, help_text="Nom de l'entreprise (pour les recruteurs)")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Candidate(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='candidate_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
