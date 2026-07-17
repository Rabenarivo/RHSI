import re
import unicodedata
import pdfplumber
import docx

def clean_text(text):
    """
    Nettoie le texte extrait d'un CV.
    - Met en minuscules.
    - Supprime la ponctuation inutile et les espaces doubles.
    - Retire les accents (ex: é -> e).
    """
    if not text:
        return ""
    
    # Mettre en minuscules
    text = text.lower()
    
    # Supprimer les accents
    # Normalisation NFD sépare les caractères de base de leurs accents
    text = ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')
    
    # Remplacer la ponctuation par des espaces (pour garder les mots séparés)
    # On conserve les caractères alphanumériques et quelques symboles utiles en tech (+, #, .)
    text = re.sub(r'[^\w\s\+#\.]', ' ', text)
    
    # Supprimer les espaces multiples
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text

def extract_text_from_pdf(pdf_path):
    """Extrait le texte d'un fichier PDF."""
    text = ""
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
    except Exception as e:
        print(f"Erreur lors de la lecture du PDF {pdf_path}: {e}")
    return text

def extract_text_from_docx(docx_path):
    """Extrait le texte d'un fichier Word (.docx)."""
    text = ""
    try:
        doc = docx.Document(docx_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
    except Exception as e:
        print(f"Erreur lors de la lecture du Word {docx_path}: {e}")
    return text

def extract_and_clean(file_path):
    """Fonction principale pour extraire et nettoyer le texte selon l'extension."""
    text = ""
    if file_path.lower().endswith('.pdf'):
        text = extract_text_from_pdf(file_path)
    elif file_path.lower().endswith('.docx'):
        text = extract_text_from_docx(file_path)
    else:
        print(f"Format non supporté: {file_path}")
        return ""
    
    return clean_text(text)
