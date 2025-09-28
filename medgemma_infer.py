from __future__ import annotations
from typing import Optional
from PIL import Image

def analyze_symptoms(img: Optional[Image.Image], symptom_text: str) -> str:
    """
    Simple stub: works with text-only (img may be None).
    Returns a textual explanation based on the user-provided symptoms.
    """
    symptom_text = (symptom_text or "").strip()
    if not symptom_text:
        return ""
    base = (
        "Based on the described symptoms "
        + ("and the visual input, " if img is not None else "(no image provided), ")
        + "this appears consistent with a mild presentation. "
        "Monitor changes (size, color, borders, pain or itch). "
        "If symptoms persist, worsen, or systemic signs occur, seek a clinician’s evaluation. "
    )
    return f"{base}\nUser-noted symptoms: {symptom_text}"
