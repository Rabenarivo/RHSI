import pdfplumber
import os

def extract_text_from_cv(file_path):
    """
    Extrait le texte d'un fichier PDF (CV) en utilisant pdfplumber.
    
    Args:
        file_path (str): Le chemin absolu ou relatif vers le fichier PDF.
        
    Returns:
        str: Le texte extrait du PDF, ou un message d'erreur si l'extraction échoue.
    """
    if not os.path.exists(file_path):
        return f"Erreur : Le fichier {file_path} est introuvable."
        
    if not file_path.lower().endswith('.pdf'):
        return "Erreur : Le fichier fourni n'est pas un PDF."

    extracted_text = []
    
    try:
        # Ouverture du fichier PDF avec pdfplumber
        with pdfplumber.open(file_path) as pdf:
            # Parcourir toutes les pages du PDF
            for page in pdf.pages:
                # Extraire le texte de chaque page
                text = page.extract_text()
                if text:
                    extracted_text.append(text)
                    
        # Joindre le texte de toutes les pages
        full_text = "\n".join(extracted_text)
        return full_text
        
    except Exception as e:
        return f"Erreur lors de l'extraction du PDF : {str(e)}"

# Code de test rapide (si vous exécutez ce fichier directement)
if __name__ == "__main__":
    # Remplacez par un chemin valide vers un de vos CV dans le dossier cvs/
    chemin_cv_test = "cvs/test_cv.pdf" 
    
    print("--- Début de l'extraction ---")
    texte = extract_text_from_cv(chemin_cv_test)
    print(texte)
    print("--- Fin de l'extraction ---")
