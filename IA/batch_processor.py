import os
import shutil
import pandas as pd
from pathlib import Path

# Importer les modules créés précédemment
from extractor import extract_and_clean
from analyzer import load_referentiel, extract_skills
from scorer import calculate_score

def process_directory(input_dir, job_requirements):
    """
    Parcourt un dossier contenant des CV, analyse chaque fichier,
    génère un rapport Excel et trie les fichiers dans des sous-dossiers.
    """
    input_path = Path(input_dir)
    if not input_path.exists() or not input_path.is_dir():
        print(f"Erreur : Le dossier {input_dir} n'existe pas.")
        return

    # Préparer les dossiers de destination
    output_dir = input_path.parent / (input_path.name + "_resultats")
    output_dir.mkdir(exist_ok=True)
    
    top_profils_dir = output_dir / "Top_Profils"
    a_verifier_dir = output_dir / "A_Verifier"
    refuses_dir = output_dir / "Refuses"
    
    for d in [top_profils_dir, a_verifier_dir, refuses_dir]:
        d.mkdir(exist_ok=True)

    referentiel = load_referentiel()
    if not referentiel:
        print("Référentiel introuvable. Annulation du traitement.")
        return

    results = []

    # Parcourir les fichiers du dossier
    for file_path in input_path.iterdir():
        if file_path.is_file() and file_path.suffix.lower() in ['.pdf', '.docx']:
            print(f"Analyse de {file_path.name}...")
            
            # 1. Extraction et nettoyage
            text = extract_and_clean(str(file_path))
            
            # 2. Analyse des compétences
            skills = extract_skills(text, referentiel)
            
            # 3. Calcul du score
            report = calculate_score(skills, job_requirements)
            
            score = report['score_percentage']
            forces = ", ".join(report['forces'])
            manques = ", ".join(report['manques'])
            
            # Ajouter aux résultats
            results.append({
                'Fichier': file_path.name,
                'Score (%)': score,
                'Forces': forces,
                'Manques': manques
            })
            
            # 4. Tri dynamique (Copie des fichiers pour ne pas altérer la source)
            try:
                if score >= 80:
                    shutil.copy2(file_path, top_profils_dir / file_path.name)
                elif score >= 50:
                    shutil.copy2(file_path, a_verifier_dir / file_path.name)
                else:
                    shutil.copy2(file_path, refuses_dir / file_path.name)
            except Exception as e:
                print(f"Erreur lors de la copie de {file_path.name}: {e}")

    # Génération du rapport Excel global
    if results:
        df = pd.DataFrame(results)
        # Trier par score décroissant
        df = df.sort_values(by='Score (%)', ascending=False)
        report_path = output_dir / "rapport_analyse.xlsx"
        df.to_excel(report_path, index=False)
        print(f"\nTraitement terminé. Rapport généré: {report_path}")
        print(f"Fichiers classés dans: {output_dir}")
    else:
        print("Aucun fichier valide trouvé dans le dossier.")
