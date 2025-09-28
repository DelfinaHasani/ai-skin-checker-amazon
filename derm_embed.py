from __future__ import annotations
from PIL import ImageStat, Image

def predict_skin_condition(img: Image.Image) -> tuple[str, float]:
    """
    Simple heuristic for demo: if the red channel clearly dominates,
    we label it as "erythema-like"; otherwise "benign-appearing".
    Returns (label, confidence 0..1).
"""


    small = img.resize((128, 128))
    stat = ImageStat.Stat(small)
    r, g, b = [float(x) for x in stat.mean[:3]]

  
    redness = max(0.0, r - (g + b) / 2.0)
    conf = max(0.0, min(1.0, redness / 50.0))

    if conf > 0.35:
        label = "erythema-like pattern"
        score = conf
    else:
        label = "benign-appearing pattern"
        score = 1.0 - conf * 0.8

    return label, float(score)
