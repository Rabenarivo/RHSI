from django import forms
from django.db.models import Q
from .models import Message
from recrutement_accounts.models import Account, Employee

class ComposeMessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-select'}),
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Sujet du message'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Écrivez votre message ici...'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ComposeMessageForm, self).__init__(*args, **kwargs)
        
        if user:
            # 1. Si Admin : on affiche tout le monde
            if user.account_type.name.lower() == 'admin':
                self.fields['recipient'].queryset = Account.objects.exclude(id=user.id).order_by('email')
                
            # 2. Si Manager ou Employé
            else:
                try:
                    employe = Employee.objects.get(account=user)
                    
                    if user.account_type.name.lower() == 'manager':
                        # Manager : Admins + son équipe (les employés dont il est le manager)
                        self.fields['recipient'].queryset = Account.objects.filter(
                            Q(account_type__name__iexact='admin') | 
                            Q(employee_profile__manager=employe)
                        ).exclude(id=user.id).order_by('email')
                        
                    elif user.account_type.name.lower() == 'employé':
                        # Employé : Admins + son manager
                        manager_account_id = employe.manager.account.id if employe.manager else None
                        self.fields['recipient'].queryset = Account.objects.filter(
                            Q(account_type__name__iexact='admin') | 
                            Q(id=manager_account_id)
                        ).exclude(id=user.id).order_by('email')
                        
                except Employee.DoesNotExist:
                    # Sécurité si un profil n'est pas complètement configuré : seulement les Admins
                    self.fields['recipient'].queryset = Account.objects.filter(account_type__name__iexact='admin').exclude(id=user.id)
                    
        self.fields['recipient'].label = "Destinataire"
        self.fields['subject'].label = "Sujet"
        self.fields['body'].label = "Message"
