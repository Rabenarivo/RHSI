from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from .forms import AccountCreationForm

def register(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.password = make_password(form.cleaned_data['password'])
            account.save()
            messages.success(request, 'Compte créé avec succès !')
            return redirect('recrutement_accounts:register')
    else:
        form = AccountCreationForm()
    
    return render(request, 'recrutement_accounts/register.html', {'form': form})
