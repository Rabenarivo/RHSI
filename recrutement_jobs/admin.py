from django.contrib import admin
from .models import JobOffer, OfferType, Application, Secteur, ExperienceRequise

admin.site.register(JobOffer)
admin.site.register(OfferType)
admin.site.register(Application)
admin.site.register(Secteur)
admin.site.register(ExperienceRequise)
