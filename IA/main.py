import os
from extractor import extract_and_clean
from analyzer import load_referentiel, extract_skills
from scorer import calculate_score

def main():
    """
    Point d'entrée principal (Terminal).
    C'est ici qu'on orchestre toutes les étapes de manière claire et séquentielle.
    """
    print("="*50)
    print("🤖 IA ANALYSEUR DE CV (Terminal Version) 🤖")
    print("="*50)
    
    # Étape A : Demander le chemin du CV à l'utilisateur
    cv_path = input("\n👉 Entrez le chemin du CV (ex: ../cvs/RAJA_CV.pdf) : ").strip()
    
    # Nettoyer les guillemets si l'utilisateur glisse-dépose le fichier dans le terminal
    cv_path = cv_path.strip('"').strip("'")
    
    if not os.path.exists(cv_path):
        print(f"❌ Erreur : Le fichier '{cv_path}' est introuvable.")
        return

    # Étape B : Définir les prérequis du poste (On pourrait aussi les demander via input)
    # Pour la pédagogie, on les définit clairement ici.
    print("\n📋 Prérequis actuels pour le poste :")
    job_requirements = [
        {'skill': 'python', 'weight': 60, 'mandatory': True},
        {'skill': 'django', 'weight': 20, 'mandatory': False},
        {'skill': 'git', 'weight': 10, 'mandatory': False},
        {'skill': 'docker', 'weight': 10, 'mandatory': False}
    ]
    for req in job_requirements:
        print(f"  - {req['skill'].capitalize()} (Poids: {req['weight']}%)")

    # Étape 1 : Extraction
    print("\n⏳ Étape 1: Lecture et nettoyage du CV...")
    cleaned_text = extract_and_clean(cv_path)
    
    if not cleaned_text:
        print("❌ Impossible d'extraire le texte du CV.")
        return

    # Étape 2 : Intelligence Lexicale (Recherche des compétences)
    print("⏳ Étape 2: Analyse lexicale (Recherche de mots-clés)...")
    referentiel = load_referentiel()
    found_skills = extract_skills(cleaned_text, referentiel)

    # Étape 3 : Scoring
    print("⏳ Étape 3: Calcul du score de compatibilité...")
    report = calculate_score(found_skills, job_requirements)

    # Affichage du bilan final
    print("\n" + "="*50)
    print("🏆 RÉSULTATS DE L'ANALYSE")
    print("="*50)
    
    score = report['score_percentage']
    
    if score >= 80:
        appreciation = "🟢 Excellent profil !"
    elif score >= 50:
        appreciation = "🟠 Profil intéressant, à vérifier."
    else:
        appreciation = "🔴 Profil insuffisant."
        
    print(f"Score final : {score}% - {appreciation}")
    
    print("\n💪 Points Forts trouvés :")
    print("  " + (", ".join(report['forces']) if report['forces'] else "Aucun"))
    
    print("\n⚠️ Compétences manquantes :")
    print("  " + (", ".join(report['manques']) if report['manques'] else "Aucune"))
    
    print("\n🧠 Détail des compétences extraites :")
    for category, skills in found_skills.items():
        if skills:
            print(f"  [{category}]: {', '.join(skills)}")
            
    print("="*50)

if __name__ == "__main__":
    main()
