# symptom_mapping.py
from rapidfuzz import fuzz, process

SYMPTOM_KEYWORDS = {
 # Cardiology
    "chest pain": "Cardiology",
    "heart pain": "Cardiology",
    "palpitations": "Cardiology",
    "irregular heartbeat": "Cardiology",
    "shortness of breath": "Cardiology",
    "high blood pressure": "Cardiology",
    "low blood pressure": "Cardiology",
    "swelling in legs": "Cardiology",

    # Neurology
    "headache": "Neurology",
    "migraine": "Neurology",
    "dizziness": "Neurology",
    "seizures": "Neurology",
    "epilepsy": "Neurology",
    "memory loss": "Neurology",
    "stroke": "Neurology",
    "weakness in limbs": "Neurology",
    "numbness": "Neurology",

    # Pulmonology
    "cough": "Pulmonology",
    "asthma": "Pulmonology",
    "wheezing": "Pulmonology",
    "lung infection": "Pulmonology",
    "tuberculosis": "Pulmonology",
    "breathing difficulty": "Pulmonology",
    "chest congestion": "Pulmonology",

    # Gastroenterology
    "stomach pain": "Gastroenterology",
    "nausea": "Gastroenterology",
    "vomiting": "Gastroenterology",
    "diarrhea": "Gastroenterology",
    "constipation": "Gastroenterology",
    "acid reflux": "Gastroenterology",
    "indigestion": "Gastroenterology",
    "bloody stool": "Gastroenterology",
    "liver pain": "Gastroenterology",

    # Orthopedics
    "joint pain": "Orthopedics",
    "fracture": "Orthopedics",
    "back pain": "Orthopedics",
    "neck pain": "Orthopedics",
    "arthritis": "Orthopedics",
    "swollen joints": "Orthopedics",
    "bone injury": "Orthopedics",

    # ENT
    "ear pain": "ENT",
    "hearing loss": "ENT",
    "ear discharge": "ENT",
    "blocked nose": "ENT",
    "sinus pain": "ENT",
    "sore throat": "ENT",
    "tonsils": "ENT",
    "nose bleeding": "ENT",

    # Dermatology
    "skin rash": "Dermatology",
    "itching": "Dermatology",
    "eczema": "Dermatology",
    "psoriasis": "Dermatology",
    "acne": "Dermatology",
    "skin infection": "Dermatology",
    "hair loss": "Dermatology",
    "dandruff": "Dermatology",
    "nail infection": "Dermatology",

    # Ophthalmology
    "eye pain": "Ophthalmology",
    "blurred vision": "Ophthalmology",
    "red eyes": "Ophthalmology",
    "watery eyes": "Ophthalmology",
    "cataract": "Ophthalmology",
    "glaucoma": "Ophthalmology",
    "double vision": "Ophthalmology",

    # Gynecology
    "menstrual pain": "Gynecology",
    "irregular periods": "Gynecology",
    "pregnancy checkup": "Gynecology",
    "infertility": "Gynecology",
    "vaginal infection": "Gynecology",
    "pelvic pain": "Gynecology",

    # Pediatrics
    "fever in child": "Pediatrics",
    "cough in child": "Pediatrics",
    "diarrhea in child": "Pediatrics",
    "vomiting in child": "Pediatrics",
    "growth delay": "Pediatrics",
    "newborn checkup": "Pediatrics",

    # Psychiatry
    "depression": "Psychiatry",
    "anxiety": "Psychiatry",
    "stress": "Psychiatry",
    "sleep disorder": "Psychiatry",
    "bipolar disorder": "Psychiatry",
    "hallucinations": "Psychiatry",

    # Nephrology
    "kidney pain": "Nephrology",
    "urine infection": "Nephrology",
    "blood in urine": "Nephrology",
    "kidney stones": "Nephrology",
    "frequent urination": "Nephrology",

    # Urology
    "prostate issues": "Urology",
    "urine blockage": "Urology",
    "painful urination": "Urology",
    "urinary retention": "Urology",

    # Endocrinology
    "diabetes": "Endocrinology",
    "thyroid problem": "Endocrinology",
    "weight loss": "Endocrinology",
    "weight gain": "Endocrinology",
    "hormonal imbalance": "Endocrinology",

    # Oncology
    "cancer checkup": "Oncology",
    "tumor": "Oncology",
    "lump in breast": "Oncology",
    "blood cancer": "Oncology",

    # Dentistry
    "tooth pain": "Dentistry",
    "cavity": "Dentistry",
    "gum bleeding": "Dentistry",
    "wisdom tooth": "Dentistry",
    "bad breath": "Dentistry",

    # General
    "fever": "General",
    "weakness": "General",
    "body ache": "General",
    "fatigue": "General",
    "cold": "General",
    "flu": "General",
    "injury": "General",
}

def match_specialty(description: str):
    """
    Map patient description to closest matching specialty.
    Uses fuzzy matching with similarity scores.
    """
    description = description.lower().strip()

    best_match, score, _ = process.extractOne(
        description,
        SYMPTOM_KEYWORDS.keys(),
        scorer=fuzz.token_sort_ratio
    )

    print(f"[DEBUG] Input: '{description}' | Best Match: '{best_match}' | Score: {score}")

    if score >= 40:
        return SYMPTOM_KEYWORDS[best_match]
    else:
        return "General"
