from __future__ import annotations
from typing import Optional
from PIL import Image
import os, torch
from transformers import pipeline

# Limito fijet në CPU për stabilitet
torch.set_num_threads(int(os.getenv("TORCH_NUM_THREADS", "2")))

_TXT = None

def _get_text_pipe():
    """TinyLlama 1.1B Chat – shumë i lehtë për CPU."""
    global _TXT
    if _TXT is not None:
        return _TXT
    device = -1  # CPU
    dtype = torch.float32
    if torch.cuda.is_available():
        device = 0
        dtype = torch.float16
    _TXT = pipeline(
        "text-generation",
        model="TinyLlama/TinyLlama-1.1B-Chat-v1.0",  # ose: "Qwen/Qwen2.5-1.5B-Instruct"
        device=device,
        torch_dtype=dtype,
    )
    return _TXT

def analyze_symptoms(img: Optional[Image.Image], symptom_text: str, max_new_tokens: int = None) -> str:
    """
    Shpjegim bazuar vetëm në tekst (model i vogël). Nëse vjen edhe foto,
    e thekson që s’analizohet nga ky model (sepse është text-only).
    """
    txt = (symptom_text or "").strip()
    if not txt and img is None:
        return ""

    max_new_tokens = max_new_tokens or int(os.getenv("TEXT_MAX_NEW_TOKENS", "80"))
    prompt = (
        "You are a careful dermatologist. Be concise and non-diagnostic. "
        "List most likely causes, self-care, and red flags for in-person care.\n"
        f"Symptoms: {txt}\nAnswer:"
    )
    try:
        out = _get_text_pipe()(
            prompt,
            max_new_tokens=max_new_tokens,
            do_sample=False,           # më shpejt dhe i qëndrueshëm
            repetition_penalty=1.05,
            pad_token_id=0
        )
        ans = out[0]["generated_text"].split("Answer:", 1)[-1].strip()
    except Exception as e:
        return f"(text-only model unavailable: {e})"

    if img is not None:
        ans += "\n\nNote: A photo was provided, but this explanation is text-only."
    return ans
