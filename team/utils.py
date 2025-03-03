import pdfplumber
import spacy
import logging

logger = logging.getLogger(__name__)

nlp = spacy.load("en_core_web_sm")

ROLE_KEYWORDS = ["Founder", "CEO", "Advisor", "Developers", "CTO", "CFO", "Team"]

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF document."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted_text = page.extract_text()
            if extracted_text:
                text += extracted_text + "\n"
    
    if not text.strip():
        logger.warning("No text was extracted from the PDF.")
    
    return text.strip()

def extract_team_info(text):
    """Extract names and roles using NLP."""
    doc = nlp(text)
    team_members = []

    for ent in doc.ents:
        if ent.label_ == "PERSON":  # Extract only names
            surrounding_text = text[max(0, ent.start_char-50): ent.end_char+50]
            for role in ROLE_KEYWORDS:
                if role.lower() in surrounding_text.lower():
                    team_members.append({"name": ent.text, "role": role})
    
    if not team_members:
        logger.warning("No team members were extracted from the document.")
    else:
        logger.info(f"Extracted team members: {team_members}")

    return team_members
