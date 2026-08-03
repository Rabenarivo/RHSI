from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import AccountCreationForm, LoginForm, AssignManagerForm, CongesForm
from .models import Account , Employee , AccountType
from django.contrib.auth.models import User
from django.contrib.admin.models import LogEntry
from .decorators import admin_required, manager_required, employe_required


def home(request):
    if request.user.is_authenticated:
        return redirect('recrutement_accounts:dashboard')
    return render(request, 'recrutement_accounts/home.html')

def register(request):
    if request.user.is_authenticated:
        return redirect('recrutement_accounts:dashboard')
        
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
    if request.user.is_authenticated:
        return redirect('recrutement_accounts:dashboard')
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('recrutement_accounts:dashboard')
            else:
                messages.error(request, 'Email ou mot de passe incorrect.')
    else:
        form = LoginForm()
        
    return render(request, 'recrutement_accounts/login.html', {'form': form})

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('recrutement_accounts:login')
        
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
            
    if account_type == 'admin':
        recent_actions = LogEntry.objects.all().select_related('content_type', 'user').order_by('-action_time')[:15]
        return render(request, 'recrutement_accounts/home_admin.html', {'recent_actions': recent_actions})
    elif account_type == 'recruteur':
        return render(request, 'recrutement_accounts/home_recruteur.html')
    elif account_type == 'candidat':
        from recrutement_jobs.models import JobOffer
        job_offers = JobOffer.objects.filter(status='active').order_by('-id')
        return render(request, 'recrutement_accounts/home_candidat.html', {'job_offers': job_offers})
    elif account_type == 'employé':
        return render(request, 'recrutement_accounts/home_employe.html')
    elif account_type == 'manager':
        from .models import LeaveRequest
        leave_requests = LeaveRequest.objects.filter(employe__manager__account__email=email_to_check).order_by('-date_demande')
        return render(request, 'recrutement_accounts/home_manager.html', {'leave_requests': leave_requests})
    else:
        return redirect('/')

def logout(request):
    auth_logout(request)
    messages.success(request, 'Vous avez été déconnecté avec succès.')
    return redirect('recrutement_accounts:login') 



@manager_required
def get_manager_emp(request):
    Employe = Employee.objects.filter(manager__account__email=request.user.username)
    return render(request, 'recrutement_accounts/get_manager_emp.html', {'Employe': Employe})

@admin_required
def assign_manager(request):
    if request.method == 'POST':
        form = AssignManagerForm(request.POST)
        if form.is_valid():
            employee = form.cleaned_data['employee']
            manager = form.cleaned_data['manager']
            
            # Save the assignment
            employee.manager = manager
            employee.save()
            
            if manager:
                messages.success(request, f"L'employé {employee} a bien été assigné au manager {manager}.")
            else:
                messages.success(request, f"Le manager de l'employé {employee} a été retiré.")
                
            return redirect('recrutement_accounts:dashboard')
    else:
        form = AssignManagerForm()
        
    return render(request, 'recrutement_accounts/assign_manager.html', {'form': form})

@employe_required
def create_conges(request):
    try:
        employe = Employee.objects.get(account__email=request.user.username)
    except Employee.DoesNotExist:
        messages.error(request, "Vous n'avez pas de profil employé.")
        return redirect('recrutement_accounts:dashboard')

    if request.method == 'POST':
        form = CongesForm(request.POST)
        if form.is_valid():
            conge = form.save(commit=False)
            conge.employe = employe
            conge.save()
            messages.success(request, "Votre demande de congé a été soumise avec succès.")
            return redirect('recrutement_accounts:dashboard')
    else:
        form = CongesForm()
        
    return render(request, 'recrutement_accounts/demande_conge.html', {'form': form, 'solde': employe.solde_conges})