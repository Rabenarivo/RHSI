def calculate_score(cv_skills, job_requirements):
    """
    Calcule le score de compatibilité entre les compétences d'un CV et les prérequis de l'offre.
    
    cv_skills: dict des compétences trouvées dans le CV (généré par analyzer.py)
               Ex: {'Langages': ['python', 'javascript'], 'Frameworks': ['django']}
    job_requirements: list de dictionnaires contenant les compétences requises et leur poids.
                      Ex: [{'skill': 'python', 'weight': 60, 'mandatory': True},
                           {'skill': 'django', 'weight': 30, 'mandatory': False},
                           {'skill': 'docker', 'weight': 10, 'mandatory': False}]
    """
    # Aplatir la liste des compétences du CV pour faciliter la recherche
    flat_cv_skills = []
    for category_skills in cv_skills.values():
        flat_cv_skills.extend(category_skills)
        
    total_weight = sum(req['weight'] for req in job_requirements)
    if total_weight == 0:
        return 0, [], []

    score = 0
    forces = []
    manques = []

    for req in job_requirements:
        skill = req['skill'].lower()
        if skill in flat_cv_skills:
            score += req['weight']
            forces.append(skill)
        else:
            manques.append(skill)
            # Pénalité supplémentaire si une compétence obligatoire manque (optionnel)
            # if req.get('mandatory', False):
            #     score -= (req['weight'] * 0.5)

    # Normaliser sur 100%
    percentage = (score / total_weight) * 100
    
    # S'assurer que le score reste entre 0 et 100
    percentage = max(0, min(100, percentage))
    
    report = {
        'score_percentage': round(percentage, 2),
        'forces': forces,
        'manques': manques
    }
    
    return report

if __name__ == "__main__":
    # Test basique
    sample_cv_skills = {
        'Langages': ['python', 'javascript'],
        'Frameworks': ['react'],
        'DevOps': ['git']
    }
    
    sample_job_reqs = [
        {'skill': 'python', 'weight': 60, 'mandatory': True},
        {'skill': 'django', 'weight': 20, 'mandatory': False},
        {'skill': 'git', 'weight': 10, 'mandatory': False},
        {'skill': 'docker', 'weight': 10, 'mandatory': False}
    ]
    
    result = calculate_score(sample_cv_skills, sample_job_reqs)
    print("Résultat du scoring :")
    print(f"Score : {result['score_percentage']}%")
    print(f"Forces : {', '.join(result['forces'])}")
    print(f"Manques : {', '.join(result['manques'])}")
