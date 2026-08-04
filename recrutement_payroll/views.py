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
