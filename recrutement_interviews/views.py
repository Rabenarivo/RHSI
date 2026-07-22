from django.shortcuts import render
from .models import Application,Interview,Contract
from django.contrib import messages

def list_application_filter(request):
    applications = Application.objects.filter(job_offer__recruteur__email=request.user.email , status="validé_recruteur")
    return render(request, 'recrutement_interviews/application_filter.html', {'applications' : applications})
def create_Interview(request,application_id):
    application = Application.objects.get(id=application_id)
    if request.method == 'POST':
        data = request.POST.dict()
        data.pop('csrfmiddlewaretoken', None)
        interview = Interview.objects.create(application=application, **data)
        messages.success(request, 'Interview created successfully')
    return render(request, 'recrutement_interviews/create_interview.html', {'application': application})

def list_interview_candidate(request):
    interviews = Interview.objects.filter(application__candidate__email=request.user.email)
    return render(request, 'recrutement_interviews/list_interview_candidate.html', {'interviews': interviews})
