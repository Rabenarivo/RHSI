from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import timedelta

from recrutement_accounts.models import AccountType, Account, Candidate
from recrutement_jobs.models import OfferType, JobOffer, Application, Secteur
from recrutement_interviews.models import Interview, Contract

class Command(BaseCommand):
    help = 'Seed database with initial data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Seeding database...')

        # 1. Create AccountTypes
        type_admin, _ = AccountType.objects.get_or_create(name='admin')
        type_recruteur, _ = AccountType.objects.get_or_create(name='recruteur')
        type_candidat, _ = AccountType.objects.get_or_create(name='candidat')

        # 2. Create OfferTypes and Categories
        offer_stage, _ = OfferType.objects.get_or_create(contract_type='stage')
        offer_cdi, _ = OfferType.objects.get_or_create(contract_type='cdi')
        offer_cdd, _ = OfferType.objects.get_or_create(contract_type='cdd')
        offer_alternance, _ = OfferType.objects.get_or_create(contract_type='alternance')

        for s in ['Informatique', 'Gestion', 'Agronomie']:
            Secteur.objects.get_or_create(name=s)

        # 3. Create Users
        raw_password = 'raja2004'
        password = make_password(raw_password) # or just password123
        
        from django.contrib.auth.models import User
        def sync_django_user(email, is_admin=False):
            if not User.objects.filter(username=email).exists():
                user = User.objects.create_user(username=email, email=email, password=raw_password)
                if is_admin:
                    user.is_staff = True
                    user.is_superuser = True
                    user.save()

        admin_acc, _ = Account.objects.get_or_create(
            email='admin@rhsi.com',
            defaults={'account_type': type_admin, 'password': password}
        )
        sync_django_user('admin@rhsi.com', is_admin=True)

        recruteur_acc, _ = Account.objects.get_or_create(
            email='recruteur@rhsi.com',
            defaults={'account_type': type_recruteur, 'password': password}
        )
        sync_django_user('recruteur@rhsi.com')

        candidat_acc, _ = Account.objects.get_or_create(
            email='candidat@rhsi.com',
            defaults={'account_type': type_candidat, 'password': password}
        )
        sync_django_user('candidat@rhsi.com')

        # 4. Create Candidate Profile
        candidat_profile, _ = Candidate.objects.get_or_create(
            account=candidat_acc,
            defaults={
                'first_name': 'Jean',
                'last_name': 'Dupont',
                'email': candidat_acc.email,
                'phone': '0123456789'
            }
        )

        # 5. Create Job Offers
        job_offer_1, _ = JobOffer.objects.get_or_create(
            title='Développeur Python/Django',
            recruteur=recruteur_acc,
            defaults={
                'offer_type': offer_cdi,
                'description': 'Nous recherchons un développeur backend avec 3 ans d\'expérience.',
                'status': 'active'
            }
        )

        job_offer_2, _ = JobOffer.objects.get_or_create(
            title='Stagiaire Data Scientist',
            recruteur=recruteur_acc,
            defaults={
                'offer_type': offer_stage,
                'description': 'Stage de fin d\'études en Machine Learning.',
                'status': 'active'
            }
        )

        # 6. Create Applications
        application_1, _ = Application.objects.get_or_create(
            job_offer=job_offer_1,
            candidate=candidat_profile,
            defaults={'status': 'validé_recruteur'}
        )

        # 7. Create Interview
        interview_1, _ = Interview.objects.get_or_create(
            application=application_1,
            defaults={
                'interview_date': timezone.now() + timedelta(days=2),
                'feedback': '',
                'status': 'planifié'
            }
        )

        # 8. Create Contract
        contract_1, _ = Contract.objects.get_or_create(
            application=application_1,
            defaults={
                'contract_type': 'cdi',
                'start_date': (timezone.now() + timedelta(days=15)).date(),
                'status': 'draft'
            }
        )

        self.stdout.write(self.style.SUCCESS('Successfully seeded the database.'))
