from django.shortcuts import render
from .models import Application,Interview,Contract
from django.contrib import messages
from django.shortcuts import redirect
from django.db.models import Prefetch

def list_application_filter(request):
    applications = Application.objects.filter(
        job_offer__recruteur__email=request.user.email, 
        status="validé_recruteur",
        contract__isnull=True
    ).prefetch_related(
        Prefetch('interviews', queryset=Interview.objects.filter(status='planifié'), to_attr='planned_interviews')
    )
    return render(request, 'recrutement_interviews/application_filter.html', {'applications' : applications})
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

def list_interview_candidate(request):
    interviews = Interview.objects.filter(application__candidate__email=request.user.email)
    return render(request, 'recrutement_interviews/list_interview_candidate.html', {'interviews': interviews})

def create_contrat(request, application_id):
    from django.shortcuts import redirect
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