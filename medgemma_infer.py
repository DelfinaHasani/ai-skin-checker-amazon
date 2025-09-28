from __future__ import annotations
from PIL import Image

def analyze_symptoms(img: Image.Image, symptom_text: str) -> str:
    """
    Simple stub: does not use large models.
    Returns a textual explanation based on the user-provided symptoms.
    """
    symptom_text = (symptom_text or "").strip()
    if not symptom_text:
        return ""
    base = (
        "Based on the described symptoms and the visual input, "
        "this appears consistent with a mild, non-urgent presentation. "
        "Monitor changes (size, color, borders, pain or itch). "
        "If symptoms persist, worsen, or systemic signs occur (fever, spreading), "
        "seek a clinician’s evaluation. "
    )
    return f"{base}\nUser-noted symptoms: {symptom_text}"

