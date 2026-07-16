from django.shortcuts import render , redirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from .forms import JobOfferForm
from .models import JobOffer , Application

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
