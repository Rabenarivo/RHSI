# Flux Complet du Système d'Information des Ressources Humaines (RHSI / SIRH)

Ce document décrit le flux de travail complet et les processus métier pour l'application RHSI (Ressources Humaines et Systèmes d'Information).

## 1. Recrutement et Intégration (Onboarding)
- **Candidatures :** Réception et gestion des candidatures (CVs, lettres de motivation).
- **Entretiens :** Planification des entretiens et suivi des évaluations des candidats.
- **Embauche :** Création du profil de l'employé dans le système, génération et signature du contrat de travail.
- **Intégration :** Attribution des ressources matérielles et accès informatiques (création de compte, emails, etc.).

## 2. Gestion Administrative du Personnel (Core RH)
- **Dossier Employé :** Centralisation des informations personnelles, bancaires et coordonnées d'urgence.
- **Contrats de Travail :** Suivi des types de contrats (CDI, CDD, Stage), des périodes d'essai et des avenants.
- **Gestion Documentaire :** Stockage sécurisé des documents administratifs (pièces d'identité, attestations, diplômes).

## 3. Gestion des Temps et des Activités (GTA)
- **Présences :** Suivi des heures de travail (pointage, feuilles de temps).
- **Absences et Congés :** 
  - Demande de congés par l'employé.
  - Notification et validation par le manager direct ou les RH.
  - Mise à jour automatique des soldes de congés.
- **Heures Supplémentaires :** Déclaration, validation et intégration pour la paie.

## 4. Préparation et Gestion de la Paie
- **Agrégation des Données :** Consolidation des salaires de base, primes, déductions pour absences, et heures supplémentaires.
- **Traitement :** Transmission des données variables de paie vers le logiciel comptable ou traitement interne.
- **Fiches de Paie :** Génération, archivage et distribution sécurisée aux employés via leur portail.

## 5. Développement RH (Performances et Compétences)
- **Évaluations :** Campagnes d'entretiens annuels et professionnels, définition et suivi des objectifs.
- **Formation :** Recueil des besoins, gestion du catalogue de formations et suivi du budget de formation.
- **Évolution de Carrière :** Gestion des promotions, mobilités internes et augmentations salariales.

## 6. Départ de l'Employé (Offboarding)
- **Démarches Administratives :** Gestion des préavis, calcul du solde de tout compte et certificats de travail.
- **Restitution :** Suivi du retour du matériel confié (ordinateur, téléphone, clés).
- **Sécurité :** Révocation automatique ou manuelle de tous les accès informatiques et physiques.

---

## Intégration dans le Projet Django (App `mere`)

Pour implémenter ce flux dans votre projet Django `RHSI` (via l'application `mere`), voici une suggestion d'architecture des modèles de données :

- **`Employe`** : Étend le modèle `User` de Django, contient les données personnelles.
- **`Departement` / `Poste`** : Structure organisationnelle de l'entreprise.
- **`Contrat`** : Lié à un employé (date de début, fin, salaire, type).
- **`Conge`** : Demandes d'absence (date début, fin, motif, statut de validation).
- **`Presence`** : Enregistrement des heures de travail quotidiennes.
- **`FicheDePaie`** : Historique et documents PDF générés mensuellement.
- **`Evaluation`** : Suivi des performances annuelles.
