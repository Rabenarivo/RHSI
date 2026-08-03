from django.shortcuts import render
from .models import Application,Interview,Contract
from django.contrib import messages
from django.shortcuts import redirect
import random
import string
from django.contrib.auth.hashers import make_password
from recrutement_accounts.models import Account, AccountType
import unicodedata
from django.contrib.auth.models import User

from recrutement_accounts.decorators import recruteur_required, candidat_required, admin_required

@recruteur_required
def list_application_filter(request):
    applications = Application.objects.filter(
        job_offer__recruteur__email=request.user.email, 
        status="validé_recruteur",
        contract__isnull=True
    )
    return render(request, 'recrutement_interviews/application_filter.html', {'applications' : applications})

@recruteur_required
def create_Interview(request,application_id):
    
    application = Application.objects.get(id=application_id)
    
    if application.interviews.filter(status='planifié').exists():
        messages.error(request, 'Un entretien est déjà planifié pour cette candidature.')
        return redirect('recrutement_interviews:application_filter')

    if request.method == 'POST':
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken', None)
        
        # Obtenir le compte recruteur connecté
        try:
            from recrutement_accounts.models import Account
            account = Account.objects.get(email=request.user.email)
            interview = Interview.objects.create(application=application, interviewer=account, **data)
        except:
            interview = Interview.objects.create(application=application, **data)
            
        messages.success(request, 'Interview created successfully')
    return render(request, 'recrutement_interviews/create_interview.html', {'application': application})

@candidat_required
def list_interview_candidate(request):
    interviews = Interview.objects.filter(application__candidate__email=request.user.email)
    return render(request, 'recrutement_interviews/list_interview_candidate.html', {'interviews': interviews})

@recruteur_required
def create_contrat(request, application_id):

    application = Application.objects.get(id=application_id)
    
    # Récupération automatique du type de contrat depuis l'offre
    default_contract_type = 'cdi'
    if application.job_offer.offer_type:
        offer_type_str = application.job_offer.offer_type.contract_type.lower()
        if 'stage' in offer_type_str:
            default_contract_type = 'stage'
        elif 'cdd' in offer_type_str:
            default_contract_type = 'cdd'
        elif 'alternance' in offer_type_str:
            default_contract_type = 'alternance'

    if request.method == 'POST':
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken', None)
        
        # S'assurer que les champs vides soient gérés correctement
        for key in ['duration_months', 'salary']:
            if not data.get(key):
                data[key] = None
        if not data.get('start_date'):
            data.pop('start_date', None)
        if not data.get('end_date'):
            data.pop('end_date', None)
            
        Contract.objects.update_or_create(
            application=application,
            defaults={
                'candidate': application.candidate,
                'job_title': application.job_offer.title,
                **data
            }
        )
        messages.success(request, 'Contrat créé avec succès.')
        return redirect('recrutement_interviews:application_filter')

    context = {
        'application': application,
        'default_contract_type': default_contract_type
    }
    return render(request, 'recrutement_interviews/create_contract.html', context)

@admin_required
def admin_contract_list(request):
    # For now, just show all contracts for admins
    contracts = Contract.objects.all().order_by('-id')
    return render(request, 'recrutement_interviews/admin_contract_list.html', {'contracts': contracts})

@admin_required
def admin_contract_detail(request, contract_id):
    

    def slugify(text):
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode('utf-8')
        return text.lower().replace(' ', '')

    contract = Contract.objects.get(id=contract_id)
    candidate = contract.candidate
    
    # Generate employee email
    first_name_slug = slugify(candidate.first_name)
    last_name_slug = slugify(candidate.last_name)
    generated_email = f"{first_name_slug}.{last_name_slug}@rhsi.com"
    
    # Check if employee account exists with this email
    is_employee_created = Account.objects.filter(email=generated_email).exists()

    if request.method == 'POST' and 'create_employee_account' in request.POST:
        if not is_employee_created:
            # Generate new password
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Get or create Employee AccountType
            try:
                emp_type = AccountType.objects.get(name__iexact='employé')
            except AccountType.DoesNotExist:
                emp_type = AccountType.objects.create(name='employé')
                
            # Create the Django User for authentication
            if not User.objects.filter(username=generated_email).exists():
                User.objects.create_user(
                    username=generated_email,
                    email=generated_email,
                    password=password,
                    first_name=candidate.first_name,
                    last_name=candidate.last_name
                )
                
            # Create the new employee account profile
            Account.objects.create(
                email=generated_email,
                password=make_password(password),
                account_type=emp_type
            )
            
            messages.success(request, f"Compte Employé et Utilisateur créés avec succès ! Email : {generated_email} | Mot de passe : {password}")
            is_employee_created = True

    context = {
        'contract': contract,
        'candidate': candidate,
        'is_employee_created': is_employee_created,
        'generated_email': generated_email
    }
    return render(request, 'recrutement_interviews/admin_contract_detail.html', context)
