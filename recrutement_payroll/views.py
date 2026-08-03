from django.shortcuts import render, redirect
from django.contrib import messages
from recrutement_accounts.decorators import admin_required
from .models import ConfigurationEntreprise
from .forms import ConfigurationEntrepriseForm

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
