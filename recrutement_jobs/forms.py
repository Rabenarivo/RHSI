from django import forms
from .models import JobOffer, Application

class JobOfferForm(forms.ModelForm):
    class Meta:
        model = JobOffer
        fields = ['title', 'entreprise', 'description', 'offer_type', 'secteur', 'niveau', 'experience']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'entreprise': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'offer_type': forms.Select(attrs={'class': 'form-select'}),
            'secteur': forms.Select(attrs={'class': 'form-select'}),
            'niveau': forms.Select(attrs={'class': 'form-select'}),
            'experience': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'title': 'Titre',
            'entreprise': 'Nom de l\'entreprise',
            'description': 'Description',
            'offer_type': 'Type d\'offre',
            'secteur': 'Secteur d\'activité',
            'niveau': 'Niveau requis',
            'experience': 'Expérience requise',
        }

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter', 'cv_file']
        widgets = {
            'cover_letter': forms.Textarea(attrs={'class': 'form-control'}),
            'cv_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'cover_letter': 'Lettre de motivation',
            'cv_file': 'CV',
        }
        