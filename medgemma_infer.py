from __future__ import annotations
from typing import Optional
from PIL import Image
from transformers import pipeline
import torch

_MM_PIPE = None

def _get_pipe():
    """
    Ngarkon një herë pipeline-in e MedGemma-s.
    Zgjedh automatikisht GPU nëse ka; ndryshe CPU.
    """
    global _MM_PIPE
    if _MM_PIPE is not None:
        return _MM_PIPE

    kwargs = {}
    if torch.cuda.is_available():
        kwargs["device"] = "cuda"
       
        try:
            major, minor = torch.cuda.get_device_capability()
            kwargs["torch_dtype"] = torch.bfloat16 if major >= 8 else torch.float16
        except Exception:
            kwargs["torch_dtype"] = torch.float16
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        kwargs["device"] = "mps"
        kwargs["torch_dtype"] = torch.float16
    else:
        kwargs["device"] = "cpu"
        kwargs["torch_dtype"] = torch.float32

    _MM_PIPE = pipeline(
        task="image-text-to-text",
        model="google/medgemma-4b-it",
        **kwargs,
    )
    return _MM_PIPE

def analyze_symptoms(img: Optional[Image.Image], symptom_text: str, max_new_tokens: int = 200) -> str:
    """
    Përdor MedGemma për shpjegim. Funksionon me:
      - vetëm tekst (img=None)
      - vetëm imazh (symptom_text bosh)
      - të dyja bashkë
    Kthen një string shpjegues. Në rast dështimi, kthen një mesazh fallback.
    """
    text = (symptom_text or "").strip()
    if not text and img is None:
        return ""

    
    messages = [
        {
            "role": "system",
            "content": [{"type": "text", "text": "You are a careful dermatologist. Be concise, non-diagnostic, and mention red flags when relevant."}]
        },
        {
            "role": "user",
            "content": []
        }
    ]
    content = []
    if text:
        content.append({"type": "text", "text": text})
    if img is not None:
        content.append({"type": "image", "image": img})
    messages[1]["content"] = content

    try:
        pipe = _get_pipe()
        out = pipe(text=messages, max_new_tokens=max_new_tokens)

       
        cand = out[0]
        if "generated_text" in cand:
            gt = cand["generated_text"]
            if isinstance(gt, list) and gt:
                last = gt[-1]
                if isinstance(last, dict) and "content" in last:
                    return str(last["content"]).strip()
                return str(gt)
            return str(gt).strip()
        if "answer" in cand:
            return str(cand["answer"]).strip()
        return str(cand).strip()
    except Exception as e:
        return f"(MedGemma unavailable: {e})"
