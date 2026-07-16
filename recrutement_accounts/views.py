from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import AccountCreationForm, LoginForm
from .models import Account
from django.contrib.auth.models import User

def register(request):
    if request.method == 'POST':
        form = AccountCreationForm(request.POST)
        if form.is_valid():
            account = form.save(commit=False)
            account.password = form.cleaned_data['password']
            account.save()           
            # Synchroniser avec le User de Django           
            if not User.objects.filter(username=account.email).exists():
                user = User.objects.create_user(
                    username=account.email,
                    email=account.email,
                    password=form.cleaned_data['password']
                )
                if account.account_type.name.lower() == 'admin':
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()
                    
            messages.success(request, 'Compte créé avec succès !')
            return redirect('recrutement_accounts:register')
    else:
        form = AccountCreationForm()
    
    return render(request, 'recrutement_accounts/register.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                try:
                    account = Account.objects.get(email=email)
                    account_type = account.account_type.name.lower()
                except Account.DoesNotExist:
                    account_type = 'inconnu'
                
                if account_type == 'admin':
                    return render(request, 'recrutement_accounts/home_admin.html')
                elif account_type == 'recruteur':
                    return render(request, 'recrutement_accounts/home_recruteur.html')
                elif account_type == 'candidat':
                    return render(request, 'recrutement_accounts/home_candidat.html')
                else:
                    return redirect('/')
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()
        
    return render(request, 'recrutement_accounts/login.html', {'form': form})

def logout(request):
    auth_logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('recrutement_accounts:login') 
