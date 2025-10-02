# services/ai_recommender.py
def analyze_symptoms(symptom_text):
    """
    Very simple prototype AI:
    - Matches keywords in symptom_text to specializations.
    - Returns specialization string.
    """
    text = symptom_text.lower()

    if any(word in text for word in ["chest", "heart", "cardiac", "breath"]):
        return "Cardiology"
    elif any(word in text for word in ["stomach", "abdomen", "liver", "digestion"]):
        return "Gastroenterology"
    elif any(word in text for word in ["brain", "headache", "neuro", "seizure"]):
        return "Neurology"
    elif any(word in text for word in ["fracture", "bone", "joint", "orthopedic"]):
        return "Orthopedics"
    else:
        return "General"
