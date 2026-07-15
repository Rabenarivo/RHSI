from django.db import models
from recrutement_jobs.models import Application

class Interview(models.Model):
    STATUS_CHOICES = [
        ('planifié', 'Planifié'),
        ('effectué', 'Effectué'),
        ('annulé', 'Annulé'),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    interview_date = models.DateTimeField()
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='planifié')

    def __str__(self):
        return f"Interview for {self.application} on {self.interview_date}"

class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_signature', 'Pending Signature'),
        ('active', 'Active'),
    ]
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='contract')
    contract_type = models.CharField(max_length=50, help_text="Copie historique du type d'offre")
    start_date = models.DateField(null=True, blank=True)
    is_start_date_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"Contract for {self.application}"
