from django.shortcuts import render , redirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import JobOfferForm , ApplicationForm
from .models import JobOffer , Application, ExperienceRequise
from .utils_pdf import extract_text_from_cv
from recrutement_accounts.models import Account, Candidate
from IA.analyzer import load_referentiel, extract_skills
from IA.scorer import calculate_score
from IA.extractor import clean_text
from recrutement_cv.models import AnalyseCV

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
            
            # --- Enregistrement des compétences requises ---
            skill_names = request.POST.getlist('skill_name')
            skill_notes = request.POST.getlist('skill_note')
            
            for name, note in zip(skill_names, skill_notes):
                if name.strip() and note.strip():
                    try:
                        ExperienceRequise.objects.create(
                            job_offer=job_offer,
                            skill=name.strip(),
                            note=int(note.strip())
                        )
                    except Exception as e:
                        print(f"Erreur lors de l'ajout de la compétence {name}: {e}")
            # -----------------------------------------------
            
            messages.success(request, 'Job offer created successfully')
            return redirect('recrutement_jobs:create_job_offer')
    else:
        form = JobOfferForm()
    return render(request, 'recrutement_jobs/create_job_offer.html', {'form': form})

def list_job_offer(request):
    job_offers = JobOffer.objects.filter(status="active")
    return render(request, 'recrutement_jobs/list_job_offer.html', {'job_offers': job_offers})

def get_applictaion_filter(request):
    # Récupérer les candidatures du candidat actuellement connecté
    applications = Application.objects.filter(candidate__account__email=request.user.email)
    return render(request, 'recrutement_jobs/application_filter.html', {'applications' : applications})

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
                    
                    # --- NOUVEAU : ANALYSE IA DU CV ---
                    # 1. Nettoyer le texte
                    cleaned_text = clean_text(texte_extrait)
                    
                    # 2. Charger le référentiel et extraire les compétences
                    referentiel = load_referentiel()
                    found_skills = extract_skills(cleaned_text, referentiel)
                    
                    # 3. Récupérer les prérequis de l'offre
                    job_requirements = []
                    for exp in job_offer.experiences_requises.all():
                        job_requirements.append({
                            'skill': exp.skill,
                            'weight': exp.note,
                            'mandatory': False
                        })
                    
                    # 4. Calculer le score
                    report = calculate_score(found_skills, job_requirements)
                    
                    # 5. Enregistrer l'analyse
                    AnalyseCV.objects.create(
                        candidat=candidate,
                        job=job_offer,
                        application=application,
                        score=report['score_percentage'],
                        cv_path=application.cv_file.name,
                        competence_candidat=found_skills,
                        forces=report['forces'],
                        manques=report['manques']
                    )
            # ---------------------------------------------
            
            messages.success(request, 'Votre candidature a été envoyée avec succès !')
            return redirect('recrutement_accounts:dashboard')
    else:
        form = ApplicationForm()
    return render(request, 'recrutement_jobs/application_postuler.html', {'form': form, 'job_offer': job_offer})




