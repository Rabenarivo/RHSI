from django.shortcuts import render , redirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import JobOfferForm , ApplicationForm
from .models import JobOffer , Application
from .utils_pdf import extract_text_from_cv
from recrutement_accounts.models import Account, Candidate

# Create your views here.

def create_job_offer(request):
    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            job_offer = form.save(commit=False)
            from recrutement_accounts.models import Account
            account = Account.objects.get(email=request.user.email)
            job_offer.recruteur = account
            job_offer.save()
            messages.success(request, 'Job offer created successfully')
            return redirect('recrutement_jobs:create_job_offer')
    else:
        form = JobOfferForm()
    return render(request, 'recrutement_jobs/create_job_offer.html', {'form': form})

def list_job_offer(request):
    job_offers = JobOffer.objects.filter(status="active")
    return render(request, 'recrutement_jobs/list_job_offer.html', {'job_offers': job_offers})

def application_postuler(request, job_offer_id):

    job_offer = JobOffer.objects.get(id=job_offer_id)

    if request.method == 'POST': 
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            
            # Fetch or create candidate profile for the logged in user
            email_to_check = request.user.email or request.user.username
            account = Account.objects.get(email=email_to_check)
            candidate, created = Candidate.objects.get_or_create(
                account=account,
                defaults={
                    'email': email_to_check, 
                    'first_name': 'Non renseigné', 
                    'last_name': 'Non renseigné', 
                    'phone': 'Non renseigné'
                }
            )
            
            application.candidate = candidate
            application.job_offer = job_offer
            application.save()
            
            # --- NOUVEAU : EXTRACTION DU TEXTE DU CV ---
            if application.cv_file:
                
                texte_extrait = extract_text_from_cv(application.cv_file.path)
                application.extracted_cv_text = texte_extrait
                application.save()
                
                # Optionnel : Afficher un message si l'extraction a marché (pour le debug)
                if not texte_extrait.startswith("Erreur"):
                    print(f"✅ Texte extrait avec succès pour {candidate.first_name} ({len(texte_extrait)} caractères).")
            # ---------------------------------------------
            
            messages.success(request, 'Votre candidature a été envoyée avec succès !')
            return redirect('recrutement_accounts:dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'recrutement_jobs/application_postuler.html', {'form': form, 'job_offer': job_offer})