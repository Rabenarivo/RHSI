from django.db import models
from recrutement_jobs.models import Application
from recrutement_accounts.models import Account

class Interview(models.Model):
    STATUS_CHOICES = [
        ('planifié', 'Planifié'),
        ('effectué', 'Effectué'),
        ('annulé', 'Annulé'),
    ]
    TYPE_CHOICES = [
        ('en_ligne', 'En ligne (Visio)'),
        ('presentiel', 'Présentiel'),
        ('telephone', 'Téléphone'),
    ]
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='interviews')
    title = models.CharField(max_length=100, default="Entretien")
    interview_type = models.CharField(max_length=50, choices=TYPE_CHOICES, default='en_ligne')
    location = models.CharField(max_length=255, blank=True, null=True, help_text="Lien Visio ou Adresse physique")
    interview_date = models.DateTimeField()
    feedback = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='planifié')

    def __str__(self):
        return f"{self.title} - {self.application} ({self.interview_date})"

from recrutement_accounts.models import Account, Candidate

class Contract(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Brouillon'),
        ('pending_signature', 'En attente de signature'),
        ('active', 'Actif'),
    ]
    CONTRACT_TYPE_CHOICES = [
        ('cdi', 'CDI'),
        ('cdd', 'CDD'),
        ('stage', 'Stage'),
        ('alternance', 'Alternance'),
    ]
    
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name='contract')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='contracts', null=True, blank=True, help_text="Lien direct vers le candidat")
    job_title = models.CharField(max_length=200, null=True, blank=True, help_text="Titre du poste (historisé)")
    
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES, default='cdi', help_text="Type de contrat (issu de l'offre)")
    duration_months = models.IntegerField(null=True, blank=True, help_text="Durée en mois (pour CDD ou Stage)")
    
    salary = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, help_text="Salaire brut mensuel/annuel")
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True, help_text="Date de fin (pour CDD ou Stage)")
    
    is_start_date_confirmed = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='draft')

    def __str__(self):
        return f"Contract for {self.application}"
