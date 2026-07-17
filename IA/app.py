import streamlit as st
import tempfile
import os
import json

from extractor import extract_and_clean
from analyzer import load_referentiel, extract_skills
from scorer import calculate_score

# Configuration de la page
st.set_page_config(page_title="IA Analyse de CV", page_icon="📄", layout="wide")

st.title("📄 Système d'Analyse de CV IA")
st.markdown("Uploadez un CV et définissez les prérequis du poste pour voir la compatibilité.")

# Colonnes pour l'interface
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Le Candidat (CV)")
    uploaded_file = st.file_uploader("Glissez un CV ici (PDF ou Docx)", type=['pdf', 'docx'])

with col2:
    st.subheader("2. L'Offre d'Emploi")
    st.markdown("Définissez les compétences attendues (Format: `competence: poids`)")
    default_reqs = "python: 60\ndjango: 20\ngit: 10\ndocker: 10"
    job_reqs_text = st.text_area("Prérequis (un par ligne)", value=default_reqs, height=150)

# Parsing des prérequis
job_requirements = []
try:
    for line in job_reqs_text.split('\n'):
        if ':' in line:
            skill, weight = line.split(':')
            job_requirements.append({
                'skill': skill.strip().lower(),
                'weight': int(weight.strip()),
                'mandatory': False # Simplification pour l'UI
            })
except Exception as e:
    st.error("Erreur dans le format des prérequis. Utilisez 'competence: poids'")

# Bouton d'analyse
if st.button("🚀 Analyser le Profil", use_container_width=True):
    if uploaded_file is not None and job_requirements:
        # Sauvegarder le fichier temporairement pour l'extracteur
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{uploaded_file.name.split('.')[-1]}") as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_path = tmp_file.name

        with st.spinner("Analyse par l'IA en cours..."):
            # 1. Extraction
            text = extract_and_clean(tmp_path)
            
            # 2. Analyse
            referentiel = load_referentiel()
            skills = extract_skills(text, referentiel)
            
            # 3. Scoring
            report = calculate_score(skills, job_requirements)
            
            # Nettoyage fichier temporaire
            os.unlink(tmp_path)

        # Affichage des résultats
        st.divider()
        st.header("📊 Résultats de l'Analyse")
        
        score_col, details_col = st.columns([1, 2])
        
        with score_col:
            score = report['score_percentage']
            # Couleur dynamique
            color = "green" if score >= 80 else "orange" if score >= 50 else "red"
            st.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 4rem;'>{score}%</h1>", unsafe_allow_html=True)
            if score >= 80:
                st.success("⭐ Top Profil !")
            elif score >= 50:
                st.warning("🧐 À Vérifier")
            else:
                st.error("❌ Refusé")

        with details_col:
            st.subheader("Points Forts")
            st.write(", ".join(report['forces']) if report['forces'] else "Aucun")
            
            st.subheader("Manques")
            st.write(", ".join(report['manques']) if report['manques'] else "Aucun")

        st.divider()
        st.subheader("🧠 JSON des Compétences Détectées")
        st.json(skills)

    else:
        st.warning("Veuillez uploader un CV et définir des prérequis.")
