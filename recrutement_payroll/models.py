from django.db import models
from recrutement_accounts.models import Employee
from datetime import datetime, date

class ConfigurationEntreprise(models.Model):
    heure_entree = models.TimeField(default='08:00', help_text="Heure officielle d'entrée")
    heure_sortie = models.TimeField(default='17:00', help_text="Heure officielle de sortie")
    debut_pause_midi = models.TimeField(default='12:00', help_text="Début de la pause déjeuner")
    fin_pause_midi = models.TimeField(default='13:00', help_text="Fin de la pause déjeuner")
    penalite_retard_par_heure = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Montant déduit par heure de retard")
    taux_journalier_absence = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, help_text="Montant déduit par jour d'absence (sans solde)")

    class Meta:
        verbose_name_plural = "Configurations Entreprise"

    def __str__(self):
        return f"Configuration (Entrée: {self.heure_entree}, Sortie: {self.heure_sortie})"

    @classmethod
    def get_config(cls):
        config, created = cls.objects.get_or_create(id=1)
        return config

class PointageEmploye(models.Model):
    employe = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='pointages')
    date = models.DateField(default=date.today)
    heure_arrivee = models.TimeField(null=True, blank=True)
    heure_depart = models.TimeField(null=True, blank=True)
    retard_minutes = models.IntegerField(default=0, help_text="Retard calculé en minutes")

    def save(self, *args, **kwargs):
        # Calcul automatique du retard
        if self.heure_arrivee:
            config = ConfigurationEntreprise.get_config()
            
            arrivee_datetime = datetime.combine(self.date, self.heure_arrivee)
            entree_officielle_datetime = datetime.combine(self.date, config.heure_entree)
            
            if arrivee_datetime > entree_officielle_datetime:
                diff = arrivee_datetime - entree_officielle_datetime
                self.retard_minutes = int(diff.total_seconds() / 60)
            else:
                self.retard_minutes = 0
                
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.employe} - {self.date} (Retard: {self.retard_minutes} min)"

class FicheDePaie(models.Model):
    MOIS_CHOICES = (
        (1, 'Janvier'), (2, 'Février'), (3, 'Mars'), (4, 'Avril'),
        (5, 'Mai'), (6, 'Juin'), (7, 'Juillet'), (8, 'Août'),
        (9, 'Septembre'), (10, 'Octobre'), (11, 'Novembre'), (12, 'Décembre')
    )

    employe = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='fiches_paie')
    mois = models.IntegerField(choices=MOIS_CHOICES)
    annee = models.IntegerField()
    
    salaire_base = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    prime_fixe = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    prime_variable = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    deduction_absences = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    deduction_retards = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    salaire_net = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    
    statut = models.CharField(max_length=20, choices=(
        ('brouillon', 'Brouillon'),
        ('valide', 'Validé'),
        ('paye', 'Payé')
    ), default='brouillon')
    
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('employe', 'mois', 'annee')
        
    def __str__(self):
        return f"Paie de {self.employe} - {self.get_mois_display()} {self.annee}"

    def calculate_net(self):
        # 1. Trouver le salaire de base depuis le contrat
        try:
            candidate = None
            if hasattr(self.employe.account, 'candidate_profile'):
                candidate = self.employe.account.candidate_profile
            else:
                # Recherche par email si l'employé a été créé indépendamment
                from recrutement_accounts.models import Candidate
                candidate = Candidate.objects.filter(email=self.employe.account.email).first()
                if not candidate:
                    candidate = Candidate.objects.filter(account__email=self.employe.account.email).first()
                    
            if candidate:
                from recrutement_interviews.models import Contract
                contrat = Contract.objects.filter(candidate=candidate).order_by('-id').first()
                if contrat and contrat.salary:
                    self.salaire_base = contrat.salary
        except Exception as e:
            print("Erreur récupération salaire:", e)
            pass
            
        config = ConfigurationEntreprise.get_config()
        
        # 2. Calculer les déductions pour absence sans solde de ce mois
        from recrutement_accounts.models import LeaveRequest
        import calendar
        _, last_day = calendar.monthrange(self.annee, self.mois)
        start_date = date(self.annee, self.mois, 1)
        end_date = date(self.annee, self.mois, last_day)
        
        absences = LeaveRequest.objects.filter(
            employe=self.employe,
            statut='approuve',
            type_conge__in=['sans_solde', 'autre'],
            date_debut__lte=end_date,
            date_fin__gte=start_date
        )
        
        jours_absence = 0
        for abs in absences:
            # Ne compter que les jours de ce mois (approximation)
            d1 = max(start_date, abs.date_debut)
            d2 = min(end_date, abs.date_fin)
            jours_absence += (d2 - d1).days + 1
            
        self.deduction_absences = jours_absence * config.taux_journalier_absence
        
        # 3. Calculer les déductions pour retards de ce mois
        pointages = PointageEmploye.objects.filter(
            employe=self.employe,
            date__range=[start_date, end_date]
        )
        
        total_retard_minutes = sum(p.retard_minutes for p in pointages)
        total_retard_heures = total_retard_minutes / 60.0
        self.deduction_retards = total_retard_heures * float(config.penalite_retard_par_heure)
        
        # 4. Calcul du Net
        net = float(self.salaire_base) + float(self.prime_fixe) + float(self.prime_variable) - float(self.deduction_absences) - float(self.deduction_retards)
        self.salaire_net = max(0, net) # Pas de salaire négatif
