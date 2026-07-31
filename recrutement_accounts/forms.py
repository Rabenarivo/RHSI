from django import forms
from .models import Account, Employee

class AssignManagerForm(forms.Form):
    employee = forms.ModelChoiceField(
        queryset=Employee.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select mb-3'}),
        label="Sélectionner l'Employé",
        help_text="L'employé qui sera encadré."
    )
    manager = forms.ModelChoiceField(
        queryset=Employee.objects.filter(account__account_type__name__iexact='manager'),
        widget=forms.Select(attrs={'class': 'form-select mb-3'}),
        label="Assigner au Manager",
        help_text="Le manager qui encadrera cet employé.",
        required=False
    )

class AccountCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Mot de passe")
    password_confirm = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirmer le mot de passe")

    class Meta:
        model = Account
        fields = ['account_type', 'entreprise', 'email']
        widgets = {
            'account_type': forms.Select(attrs={'class': 'form-select', 'id': 'id_account_type'}),
            'entreprise': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_entreprise'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'account_type': 'Type de compte',
            'entreprise': 'Nom de l\'entreprise',
            'email': 'Adresse E-mail',
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        account_type = cleaned_data.get("account_type")
        entreprise = cleaned_data.get("entreprise")

        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', "Les mots de passe ne correspondent pas.")
            
        if account_type and account_type.name.lower() == 'recruteur' and not entreprise:
            self.add_error('entreprise', "Le nom de l'entreprise est obligatoire pour un recruteur.")

        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}), label="Adresse E-mail")
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Mot de passe")