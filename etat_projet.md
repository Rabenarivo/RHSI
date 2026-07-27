# État d'Avancement du Projet RHSI (SIRH)

Ce document résume ce qui a été accompli jusqu'à présent et détaille la feuille de route pour les étapes restantes.

## ✅ Ce qui est déjà fini

### 1. Le Moteur d'Intelligence Artificielle pour les CV (`dossier IA/`)
Le système complet d'analyse de CV décrit dans le processus technique a été réalisé :
- **Extraction :** Lecture et nettoyage de texte depuis des fichiers PDF et Word (`extractor.py`).
- **Analyse Lexicale :** Détection de compétences basées sur un dictionnaire de synonymes (`analyzer.py`, `referentiel.json`).
- **Scoring Avancé :** Calcul du pourcentage de correspondance entre un profil et les exigences du poste (`scorer.py`).
- **Traitement par lot :** Analyse automatique de dossiers entiers pour générer des tableaux de résultats (Excel) et trier les candidats (`batch_processor.py`).
- **Interface Console :** Outil de ligne de commande permettant d'exécuter l'analyse facilement (`main.py`).

### 2. Le Module Recrutement (Partie 1 du Flux SIRH)
Les fondations de l'application web Django pour la partie recrutement sont en place, réparties en 4 applications :
- **`recrutement_accounts` :** Gestion des utilisateurs, des sessions, avec séparation des rôles (candidat vs recruteur) et des tableaux de bord.
- **`recrutement_jobs` :** Création et affichage des offres d'emploi par les recruteurs.
- **`recrutement_cv` :** Gestion des dépôts de CV par les candidats.
- **`recrutement_interviews` :** Planification d'entretiens et système de filtre des candidatures.

---

## ⏳ Ce qui reste à faire

### 1. Intégration Finale de l'IA (Module Recrutement)
- **Automatisation :** Connecter le moteur d'analyse de CV (`IA/`) directement dans les vues Django de `recrutement_cv` ou `recrutement_interviews`. L'objectif est que les CV téléchargés par les candidats soient automatiquement scorés par le système sans intervention manuelle.

### 2. Développement de l'Application Core RH (Administration)
- **Modèle `Employe` :** Création d'une entité étendant le compte utilisateur une fois le candidat embauché, avec gestion des informations personnelles, bancaires et coordonnées d'urgence.
- **Gestion des Contrats :** Suivi des types de contrats (CDI, CDD, Stage), des périodes d'essai et stockage des documents administratifs associés.

### 3. Module GTA (Gestion des Temps et des Activités)
- **Présences (`Presence`) :** Système de pointage ou d'enregistrement des heures de travail quotidiennes/hebdomadaires.
- **Congés (`Conge`) :** Mise en place d'un flux de demande d'absence par l'employé avec un système de validation par le manager, et mise à jour automatique des soldes.

### 4. Module Préparation et Gestion de la Paie
- **Agrégation :** Calcul automatique basé sur les heures travaillées (GTA), les absences, et les heures supplémentaires.
- **Fiche de Paie (`FicheDePaie`) :** Génération (idéalement au format PDF), archivage et distribution sécurisée aux employés via leur portail.

### 5. Module Développement RH (Performances)
- **Évaluations (`Evaluation`) :** Suivi des performances annuelles, définition d'objectifs, et gestion d'un catalogue de formations pour la montée en compétences.

### 6. Module Offboarding (Départs)
- **Démarches :** Processus administratif pour le départ de l'employé (préavis, solde de tout compte).
- **Sécurité :** Révocation des accès informatiques et suivi de la restitution du matériel confié.
