from django.db import models
from recrutement_accounts.models import Account, Candidate
from django.core.exceptions import ValidationError

class OfferType(models.Model):
    contract_type = models.CharField(max_length=50, help_text="stage, cdi, cdd, alternance")

    def __str__(self):
        return self.contract_type

class Secteur(models.Model):
    name = models.CharField(max_length=100,null=True, help_text="ex: informatique, gestion, agronomie")

    def __str__(self):
        return self.name

class JobOffer(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('closed', 'Closed'),
    ]
    NIVEAU_CHOICES = [
        ('1', 'L1'), ('2', 'L2'), ('3', 'L3'), ('4', 'M1'), ('5', 'M2'),
    ]
    EXPERIENCE_CHOICES = [
        ('1', '1 an'), ('2', '2 ans'), ('3', '3 ans'), ('4', '4 ans'), ('5', '5 ans et plus'),
    ]
    recruteur = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='job_offers', help_text="Référence au recruteur")
    entreprise = models.CharField(max_length=100, null=True, blank=True, help_text="Entreprise proposant l'offre")
    offer_type = models.ForeignKey(OfferType, on_delete=models.SET_NULL, null=True, related_name='job_offers')
    secteur = models.ForeignKey(Secteur, on_delete=models.SET_NULL, null=True, blank=True, related_name='job_offers')
    niveau = models.CharField(max_length=50, choices=NIVEAU_CHOICES, null=True, blank=True)
    experience = models.CharField(max_length=50, choices=EXPERIENCE_CHOICES, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return self.title

class ExperienceRequise(models.Model):
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='experiences_requises')
    skill = models.CharField(max_length=100, help_text="ex: JS, JAVA")
    note = models.PositiveIntegerField(help_text="ex: 10, 20. Le total pour une offre ne doit pas dépasser 100")

    def clean(self):
        super().clean()
        if self.job_offer_id:
            existing_experiences = self.job_offer.experiences_requises.exclude(pk=self.pk)
            total_note = existing_experiences.aggregate(total=models.Sum('note'))['total'] or 0
            if total_note + (self.note or 0) > 100:
                raise ValidationError(f"La somme totale des notes d'expérience ne doit pas dépasser 100. Le total actuel est de {total_note}.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.skill} ({self.note}) pour {self.job_offer}"

class Application(models.Model):
    STATUS_CHOICES = [
        ('postulé', 'Postulé'),
        ('validé_recruteur', 'Validé Recruteur'),
        ('refusé', 'Refusé'),
    ]
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='postulé')
    cover_letter = models.TextField(null=True, blank=True, help_text="Lettre de motivation")
    cv_file = models.FileField(upload_to='cvs/', null=True, blank=True, help_text="CV")
    extracted_cv_text = models.TextField(null=True, blank=True, help_text="Texte extrait automatiquement du CV")
    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Application of {self.candidate} for {self.job_offer}"
