# tiny_llama.py
from __future__ import annotations
from typing import Optional, Tuple, Dict, List
from PIL import Image, ImageStat
import numpy as np
import re


def _redness_score(img: Image.Image) -> float:
    """0..1 heuristic redness dominance."""
    small = img.convert("RGB").resize((128, 128))
    stat = ImageStat.Stat(small)
    r, g, b = [float(x) for x in stat.mean[:3]]
    redness = max(0.0, r - (g + b) / 2.0) 
    return float(max(0.0, min(1.0, redness / 50.0)))

def _texture_score(img: Image.Image) -> float:
    """0..1 rough texture proxy via grayscale std-dev."""
    g = img.convert("L").resize((128, 128))
    arr = np.asarray(g, dtype=np.float32) / 255.0
    std = float(arr.std()) 
    return max(0.0, min(1.0, (std - 0.08) / 0.22))


_CONDITION_KEYWORDS: Dict[str, List[str]] = {
    "psoriasis-like pattern": [
        r"\bpsoriasis\b", r"\bplaque(?:s)?\b", r"\bscal(?:y|es|ing)\b",
        r"\bsilvery\b", r"\bwell[- ]?demarcated\b", r"\belbows?\b", r"\bknees?\b",
        r"\bextensor\b", r"\bthick\b"
    ],
    "eczema-like pattern": [
        r"\beczema\b", r"\bdermatitis\b", r"\bitch(?:y|ing)\b", r"\bxerosis\b",
        r"\bflexural\b", r"\bbehind the knees\b", r"\belbows?\b", r"\bpatch(?:es)?\b"
    ],
    "tinea-like pattern": [
        r"\btinea\b", r"\bfungal\b", r"\bringworm\b", r"\bannular\b", r"\bcentral clearing\b",
        r"\bscaly edge\b"
    ],
    "acne-like pattern": [
        r"\bacne\b", r"\bpimple(?:s)?\b", r"\bcomedone(?:s)?\b", r"\bpapule(?:s)?\b", r"\bpustule(?:s)?\b"
    ],
    "urticaria-like pattern": [
        r"\bhives\b", r"\burticaria\b", r"\bwelts?\b", r"\btransient\b", r"\bmigratory\b", r"\bwheal(?:s)?\b"
    ],
}

def _score_text_for_conditions(text: str) -> Tuple[str, float, Dict[str, int]]:
    text_l = text.lower()
    best_label, best_hits = None, -1
    hit_map: Dict[str, int] = {}
    for label, patterns in _CONDITION_KEYWORDS.items():
        hits = sum(1 for p in patterns if re.search(p, text_l))
        hit_map[label] = hits
        if hits > best_hits:
            best_label, best_hits = label, hits
    conf = 0.0 if best_hits <= 0 else min(1.0, 0.25 * best_hits)
    return best_label or "", conf, hit_map


def _compose_paragraph(diagnosis: Optional[str],
                       reasons: List[str],
                       user_text: str,
                       add_safety: bool = True) -> str:
    parts = []
    if diagnosis:
        parts.append(f"From the picture you uploaded, it seems like {diagnosis}.")
    if user_text.strip():
        parts.append(f"Considering your notes (“{user_text.strip()}”), here’s a combined, non-diagnostic explanation.")
    if reasons:
        parts.append("This impression comes from " + ", ".join(reasons) + ".")

    parts.append("Track changes over time (size, borders, color, scale, itch/pain). "
                 "Use gentle skincare and avoid known triggers or harsh products. "
                 "Seek in-person evaluation if lesions spread rapidly, bleed, become very painful, "
                 "or you develop fever or systemic symptoms.")
    if add_safety:
        parts.append("This is not a diagnosis; a clinician’s exam is required for confirmation.")

    paragraph = " ".join(s.rstrip(" .") + "." for s in parts if s.strip())
    return paragraph


def analyze_symptoms(img: Optional[Image.Image],
                     symptom_text: str,
                     disease_hint: Optional[str] = None,
                     accuracy_hint: Optional[float] = None,
                     length: str = "short") -> str:
    """
    Returns a single, cohesive paragraph using both image cues and text.
    - If img is provided, uses redness + texture as cues.
    - Uses keyword scoring to bias toward psoriasis/etc.
    - disease_hint/accuracy_hint come from your quick image classifier (optional).
    """
    symptom_text = (symptom_text or "").strip()
 
    txt_label, txt_conf, hits = _score_text_for_conditions(symptom_text)


    reasons = []
    img_label = None
    if img is not None:
        r = _redness_score(img)
        t = _texture_score(img)
        if r > 0.35: reasons.append("prominent erythema")
        if t > 0.35: reasons.append("coarse/scaly surface texture")
        if r > 0.35 and t > 0.40:
            img_label = "psoriasis-like pattern"
        elif r > 0.35:
            img_label = "erythema-like pattern"

        if disease_hint:
            reasons.append(f"the classifier’s cue ({disease_hint}{f', {accuracy_hint:.0%}' if isinstance(accuracy_hint, float) else ''})")

    label_candidates = []
    if txt_conf >= 0.5 and txt_label: 
        label_candidates.append((txt_label, txt_conf + 0.2))
    if img_label:
        label_candidates.append((img_label, 0.5))
    if disease_hint:
        label_candidates.append((disease_hint, 0.35))
    label = None
    if label_candidates:
        label = sorted(label_candidates, key=lambda x: x[1], reverse=True)[0][0]

 
    if re.search(r"\bpsoriasis\b", symptom_text.lower()):
        label = "psoriasis-like pattern"

    if label == "psoriasis-like pattern":
        if "coarse/scaly surface texture" not in reasons:
            reasons.append("patchy scale or plaque-like texture on review")

    if length.lower() in {"long", "longer"}:
        reasons.append("the overall distribution and chronic-sounding course you described")

    return _compose_paragraph(label, reasons, symptom_text)
