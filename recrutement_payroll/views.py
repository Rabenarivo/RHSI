from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import timezone
from recrutement_accounts.decorators import admin_required, employe_required
from .models import ConfigurationEntreprise, PointageEmploye
from .forms import ConfigurationEntrepriseForm
from recrutement_accounts.models import Employee

@admin_required
def edit_configuration(request):
    config = ConfigurationEntreprise.get_config()
    
    if request.method == 'POST':
        form = ConfigurationEntrepriseForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Les paramètres de l'entreprise ont été mis à jour avec succès.")
            return redirect('recrutement_accounts:dashboard')
    else:
        form = ConfigurationEntrepriseForm(instance=config)
        
    return render(request, 'recrutement_payroll/edit_configuration.html', {'form': form})

@employe_required
def pointage_action(request):
    if request.method == 'POST':
        email_to_check = request.user.email or request.user.username
        try:
            employe = Employee.objects.get(account__email=email_to_check)
        except Employee.DoesNotExist:
            messages.error(request, "Profil employé introuvable. Impossible de pointer.")
            return redirect('recrutement_accounts:dashboard')
            
        today = timezone.localdate()
        now_time = timezone.localtime().time()
        
        pointage, created = PointageEmploye.objects.get_or_create(
            employe=employe, 
            date=today
        )
        
        if created or not pointage.heure_arrivee:
            pointage.heure_arrivee = now_time
            pointage.save()
            messages.success(request, f"Pointage d'arrivée enregistré à {now_time.strftime('%H:%M')}. Retard calculé: {pointage.retard_minutes} min.")
        elif not pointage.heure_depart:
            pointage.heure_depart = now_time
            pointage.save()
            messages.success(request, f"Pointage de départ enregistré à {now_time.strftime('%H:%M')}")
        else:
            messages.warning(request, "Vous avez déjà pointé votre arrivée et votre départ aujourd'hui.")
            
    return redirect('recrutement_accounts:dashboard')

@admin_required
def admin_list_payroll(request):
    # Affiche toutes les fiches de paie, par ordre décroissant
    from .models import FicheDePaie
    payrolls = FicheDePaie.objects.all().order_by('-annee', '-mois', 'employe__account__email')
    return render(request, 'recrutement_payroll/admin_list_payroll.html', {'payrolls': payrolls})

@admin_required
def generate_payroll(request):
    from django.utils import timezone
    from .models import FicheDePaie
    from recrutement_accounts.models import Employee
    
    if request.method == 'POST':
        today = timezone.localdate()
        mois_courant = today.month
        annee_courante = today.year
        
        employes = Employee.objects.all()
        count_created = 0
        count_updated = 0
        
        for employe in employes:
            fiche, created = FicheDePaie.objects.get_or_create(
                employe=employe,
                mois=mois_courant,
                annee=annee_courante
            )
            fiche.calculate_net()
            fiche.save()
            
            if created:
                count_created += 1
            else:
                count_updated += 1
                
        messages.success(request, f"Génération terminée : {count_created} fiches créées, {count_updated} fiches mises à jour pour {mois_courant}/{annee_courante}.")
        
    return redirect('recrutement_payroll:admin_list_payroll')

@employe_required
def employee_list_payroll(request):
    from .models import FicheDePaie
    email_to_check = request.user.email or request.user.username
    payrolls = FicheDePaie.objects.filter(employe__account__email=email_to_check, statut__in=['valide', 'paye']).order_by('-annee', '-mois')
    
    # Si le manager veut voir aussi ses fiches (manager_required passe aussi)
    return render(request, 'recrutement_payroll/employee_list_payroll.html', {'payrolls': payrolls})

def payslip_detail(request, slip_id):
    # L'admin ou le propriétaire de la fiche peut la voir
    from django.shortcuts import get_object_or_404
    from .models import FicheDePaie
    
    fiche = get_object_or_404(FicheDePaie, id=slip_id)
    email_to_check = request.user.email or request.user.username
    
    # Vérification des droits (Admin ou propriétaire)
    if request.session.get('account_type') != 'admin' and fiche.employe.account.email != email_to_check:
        messages.error(request, "Accès refusé. Vous ne pouvez voir que vos propres fiches de paie.")
        return redirect('recrutement_accounts:dashboard')
        
    return render(request, 'recrutement_payroll/payslip_detail.html', {'fiche': fiche})

