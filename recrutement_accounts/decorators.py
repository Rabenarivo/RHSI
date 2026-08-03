from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps
from .models import Account

def get_user_role(request):
    account_type = request.session.get('account_type')
    if not account_type:
        try:
            email_to_check = request.user.email or request.user.username
            account = Account.objects.get(email=email_to_check)
            account_type = account.account_type.name.lower()
        except Account.DoesNotExist:
            if request.user.is_superuser or request.user.is_staff:
                account_type = 'admin'
            else:
                account_type = 'candidat'
        request.session['account_type'] = account_type
    return account_type

def role_required(allowed_roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('recrutement_accounts:login')
            
            account_type = get_user_role(request)
                
            # Les admins ont accès à toutes les pages protégées par un rôle (sauf cas très spécifiques si on le souhaite)
            # Mais par précaution, on va vérifier si 'admin' est autorisé, ou on laisse l'accès total à l'admin.
            # On va donner l'accès total à l'admin pour simplifier, sauf pour l'espace candidat
            if account_type in allowed_roles or (account_type == 'admin' and 'candidat' not in allowed_roles):
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Accès refusé. Vous n'avez pas le rôle requis pour voir cette page.")
                return redirect('recrutement_accounts:dashboard')
        return _wrapped_view
    return decorator

# Création des décorateurs spécifiques pour chaque rôle
admin_required = role_required(['admin'])
manager_required = role_required(['manager'])
employe_required = role_required(['employé', 'manager']) # Le manager peut aussi avoir accès aux pages employé
recruteur_required = role_required(['recruteur'])
candidat_required = role_required(['candidat'])
