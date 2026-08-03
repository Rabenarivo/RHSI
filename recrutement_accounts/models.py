from django.db import models

class AccountType(models.Model):
    ACCOUNT_TYPES = (
        ('admin', 'Admin'),
        ('recruteur', 'Recruteur'),
        ('candidat', 'Candidat'),
        ('employé', 'Employé'),
        ('manager', 'Manager'),
    )
    name = models.CharField(max_length=50, choices=ACCOUNT_TYPES, help_text="Sélectionnez le type de compte")

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

class Employee(models.Model):
    account = models.OneToOneField(Account, on_delete=models.CASCADE, related_name='employee_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    manager = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='subordinates', help_text="Le manager qui encadre cet employé")
    solde_conges = models.FloatField(default=30.0, help_text="Solde de congés (en jours)")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class LeaveRequest(models.Model):
    STATUS_CHOICES = (
        ('en_attente', 'En attente'),
        ('approuve', 'Approuvé'),
        ('refuse', 'Refusé'),
    )

    LEAVE_TYPES = (
        ('conge_paye', 'Congé payé'),
        ('maladie', 'Maladie'),
        ('maternite', 'Maternité'),
        ('paternite', 'Paternité'),
        ('sans_solde', 'Sans solde'),
        ('autre', 'Autre'),
    )

    employe = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    type_conge = models.CharField(max_length=50, choices=LEAVE_TYPES, default='conge_paye')
    date_debut = models.DateField()
    date_fin = models.DateField()
    motif = models.TextField(blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    date_demande = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande de {self.employe} du {self.date_debut} au {self.date_fin}"
    
    @property
    def duree(self):
        if self.date_debut and self.date_fin:
            # +1 car du lundi au lundi inclus fait 1 jour
            return (self.date_fin - self.date_debut).days + 1
        return 0
