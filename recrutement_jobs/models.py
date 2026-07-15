from django.db import models
from recrutement_accounts.models import Account, Candidate

class OfferType(models.Model):
    contract_type = models.CharField(max_length=50, help_text="stage, cdi, cdd, alternance")

    def __str__(self):
        return self.contract_type

class JobOffer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    recruteur = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='job_offers', help_text="Référence au recruteur")
    offer_type = models.ForeignKey(OfferType, on_delete=models.SET_NULL, null=True, related_name='job_offers')
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = [
        ('postulé', 'Postulé'),
        ('validé_recruteur', 'Validé Recruteur'),
        ('refusé', 'Refusé'),
    ]
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='postulé')
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application of {self.candidate} for {self.job_offer}"
