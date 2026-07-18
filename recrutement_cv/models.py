from django.db import models
from recrutement_accounts.models import Candidate
from recrutement_jobs.models import JobOffer, Application

class AnalyseCV(models.Model):
    candidat = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='analyses_cv', help_text="Le candidat lié à ce CV")
    job = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='analyses_cv', help_text="L'offre d'emploi pour laquelle le CV est analysé")
    application = models.OneToOneField(Application, on_delete=models.SET_NULL, null=True, blank=True, related_name='analyse_cv', help_text="La candidature complète liée (optionnel mais recommandé)")
    
    score = models.FloatField(help_text="Pourcentage de compatibilité (0 à 100)")
    cv_path = models.CharField(max_length=500, help_text="Chemin ou nom du fichier CV physique")
    
    competence_candidat = models.JSONField(help_text="Dictionnaire des compétences trouvées classées par catégories")
    forces = models.JSONField(default=list, help_text="Liste des compétences requises trouvées")
    manques = models.JSONField(default=list, help_text="Liste des compétences requises manquantes")
    
    date_analyse = models.DateTimeField(auto_now_add=True, help_text="Date à laquelle l'analyse a été effectuée")

    def __str__(self):
        return f"Analyse de {self.candidat} pour {self.job} - Score: {self.score}%"
