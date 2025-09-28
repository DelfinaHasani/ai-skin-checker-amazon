from __future__ import annotations
from io import BytesIO
from typing import Tuple
from PIL import Image, ImageStat
from huggingface_hub import from_pretrained_keras
import tensorflow as tf
import numpy as np

_DERM_MODEL = None

def _load_derm_model():
    global _DERM_MODEL
    if _DERM_MODEL is None:
        _DERM_MODEL = from_pretrained_keras("google/derm-foundation")
    return _DERM_MODEL

def _pil_to_tfexample_bytes(img: Image.Image) -> bytes:
    """It returns a PIL Image in tf.train.Example serialized."""
    buf = BytesIO()
    img.convert("RGB").save(buf, "PNG")
    image_bytes = buf.getvalue()
    example = tf.train.Example(features=tf.train.Features(
        feature={
            "image/encoded": tf.train.Feature(
                bytes_list=tf.train.BytesList(value=[image_bytes])
            )
        }
    ))
    return example.SerializeToString()

def derm_embedding(img: Image.Image) -> np.ndarray:
    """
    Nxjerr embedding nga Derm Foundation (vector 1D).
    """
    model = _load_derm_model()
    infer = model.signatures["serving_default"]
    ex_bytes = _pil_to_tfexample_bytes(img)
    out = infer(inputs=tf.constant([ex_bytes]))
    emb = out["embedding"].numpy().flatten()
    return emb

def predict_skin_condition(img: Image.Image) -> Tuple[str, float]:
    """
    Klasifikim i thjeshtë (heuristik) për të kthyer (label, score) menjëherë,
    ndërsa Derm Foundation përdoret për embedding.
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

