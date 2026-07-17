import json
import re
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def load_referentiel(filepath="referentiel.json"):
    """Charge le dictionnaire des compétences depuis le fichier JSON."""
    full_path = os.path.join(BASE_DIR, filepath)
    if not os.path.exists(full_path):
        print(f"Erreur : Le fichier {full_path} est introuvable.")
        return {}
    
    with open(full_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def extract_skills(cleaned_text, referentiel):
    """
    Parcourt le texte nettoyé et recherche les compétences en utilisant des Regex 
    basées sur les alias du référentiel.
    Retourne un dictionnaire avec les compétences trouvées par catégorie.
    """
    skills_found = {category: [] for category in referentiel.keys()}
    
    for category, skills in referentiel.items():
        for skill_name, aliases in skills.items():
            for alias in aliases:
                # \b assure que l'on matche un mot entier (évite de matcher "js" dans "bonjourjs")
                # On échappe l'alias car il peut contenir des caractères spéciaux comme C++ ou Node.js
                pattern = r'\b' + re.escape(alias) + r'\b'
                
                # Si l'alias est trouvé dans le texte, on ajoute la compétence principale (si elle n'y est pas déjà)
                if re.search(pattern, cleaned_text):
                    if skill_name not in skills_found[category]:
                        skills_found[category].append(skill_name)
                    # Dès qu'un alias de la compétence est trouvé, on passe à la compétence suivante
                    break
                    
    # Nettoyer le dictionnaire pour enlever les catégories vides (optionnel)
    return {cat: skills for cat, skills in skills_found.items() if skills}
