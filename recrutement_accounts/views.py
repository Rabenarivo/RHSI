from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import AccountCreationForm, LoginForm, AssignManagerForm, CongesForm
from .models import Account , Employee , AccountType , LeaveRequest
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
        from .models import LeaveRequest
        from recrutement_payroll.models import PointageEmploye
        from django.utils import timezone
        
        try:
            employe = Employee.objects.get(account__email=email_to_check)
            mes_conges = LeaveRequest.objects.filter(employe=employe).order_by('-date_demande')
            
            # Pointage du jour
            today = timezone.localdate()
            pointage_jour = PointageEmploye.objects.filter(employe=employe, date=today).first()
            
        except Employee.DoesNotExist:
            employe = None
            mes_conges = []
            pointage_jour = None
            
        return render(request, 'recrutement_accounts/home_employe.html', {
            'employe': employe, 
            'mes_conges': mes_conges,
            'pointage_jour': pointage_jour
        })
        
    elif account_type == 'manager':
        from .models import LeaveRequest
        from recrutement_payroll.models import PointageEmploye
        from django.utils import timezone
        
        today = timezone.localdate()
        
        try:
            employe_manager = Employee.objects.get(account__email=email_to_check)
            pointage_jour = PointageEmploye.objects.filter(employe=employe_manager, date=today).first()
        except Employee.DoesNotExist:
            pointage_jour = None
            
        leave_requests = LeaveRequest.objects.filter(employe__manager__account__email=email_to_check).order_by('-date_demande')
        
        # Pointages de l'équipe pour aujourd'hui
        pointages_equipe = PointageEmploye.objects.filter(
            employe__manager__account__email=email_to_check,
            date=today
        ).order_by('employe__first_name')
        
        return render(request, 'recrutement_accounts/home_manager.html', {
            'leave_requests': leave_requests,
            'pointage_jour': pointage_jour,
            'pointages_equipe': pointages_equipe
        })
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

@manager_required
def change_leave_status(request, leave_id, status):
    from .models import LeaveRequest
    leave_request = get_object_or_404(LeaveRequest, id=leave_id)
    
    # Sécurité : Vérifier que le manager connecté est bien le manager de cet employé
    if leave_request.employe.manager.account.email != request.user.email and leave_request.employe.manager.account.email != request.user.username:
        messages.error(request, "Vous n'avez pas l'autorisation de modifier cette demande.")
        return redirect('recrutement_accounts:dashboard')
        
    if status in ['approuve', 'refuse']:
        # Si on approuve, on déduit le solde de congés (seulement si ce n'est pas déjà approuvé pour éviter la double déduction)
        if status == 'approuve' and leave_request.statut != 'approuve':
            # On pourrait rajouter une vérification pour ne déduire que certains types de congés (LeaveType.deductible)
            # Mais comme on a remplacé LeaveType par un Choice, on va déduire pour tous par défaut sauf "sans_solde"
            if leave_request.type_conge != 'sans_solde':
                if leave_request.employe.solde_conges >= leave_request.duree:
                    leave_request.employe.solde_conges -= leave_request.duree
                    leave_request.employe.save()
                else:
                    messages.error(request, f"L'employé n'a pas assez de jours de congés (Solde: {leave_request.employe.solde_conges}, Requis: {leave_request.duree}).")
                    return redirect('recrutement_accounts:dashboard')
                    
        # Si c'était approuvé et qu'on le passe en refusé/en_attente, on devrait rembourser le solde
        elif status != 'approuve' and leave_request.statut == 'approuve':
            if leave_request.type_conge != 'sans_solde':
                leave_request.employe.solde_conges += leave_request.duree
                leave_request.employe.save()
                
        leave_request.statut = status
        leave_request.save()
        messages.success(request, f"Le statut de la demande a été mis à jour ({status}).")
        
    return redirect('recrutement_accounts:dashboard')