from django.contrib import admin
from .models import ConfigurationEntreprise, PointageEmploye, FicheDePaie

@admin.register(ConfigurationEntreprise)
class ConfigurationEntrepriseAdmin(admin.ModelAdmin):
    list_display = ('heure_entree', 'heure_sortie', 'penalite_retard_par_heure', 'taux_journalier_absence')

@admin.register(PointageEmploye)
class PointageEmployeAdmin(admin.ModelAdmin):
    list_display = ('employe', 'date', 'heure_arrivee', 'heure_depart', 'retard_minutes')
    list_filter = ('date', 'employe')

@admin.register(FicheDePaie)
class FicheDePaieAdmin(admin.ModelAdmin):
    list_display = ('employe', 'mois', 'annee', 'salaire_base', 'salaire_net', 'statut')
    list_filter = ('mois', 'annee', 'statut')
    
    def save_model(self, request, obj, form, change):
        # Calculer le net automatiquement avant de sauvegarder depuis l'admin
        obj.calculate_net()
        super().save_model(request, obj, form, change)
