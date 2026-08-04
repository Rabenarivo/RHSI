from django import forms
from .models import ConfigurationEntreprise

class ConfigurationEntrepriseForm(forms.ModelForm):
    class Meta:
        model = ConfigurationEntreprise
        fields = ['heure_entree', 'heure_sortie', 'debut_pause_midi', 'fin_pause_midi', 'penalite_retard_par_heure', 'taux_journalier_absence']
        widgets = {
            'heure_entree': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'heure_sortie': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'debut_pause_midi': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'fin_pause_midi': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'penalite_retard_par_heure': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'taux_journalier_absence': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
        }
