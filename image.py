from __future__ import annotations
import os, re
from typing import Optional
import numpy as np
from PIL import Image

os.environ.setdefault("TRANSFORMERS_NO_TF", "1")

VQA_MODEL_ID  = os.getenv("VQA_MODEL_ID",  "Salesforce/blip-vqa-base")
CAP_MODEL_ID1 = os.getenv("CAP_MODEL_ID1", "Salesforce/blip-image-captioning-base")
MAX_NEW = int(os.getenv("CAPTION_MAX_NEW_TOKENS", "128")) 

_vqa = None
_cap1 = None

TRIVIAL = {"no","none","unknown","n/a","na","nothing","cannot tell","can't tell","unsure"}
GENERIC_BAD = {"person","man","woman","boy","girl","towel","hat","phone","bathroom","mirror","kitchen","sofa"}
DERM_HINT_GOOD = {"skin","lesion","rash","red","erythema","plaque","patch","scaly","scale","flaky","itch","border",
                  "demarcated","ill-defined","crust","ulcer","vesicle","pustule","papule","hyperpigmented","hypopigmented"}

def _looks_trivial(s:str)->bool:
    if not s: return True
    t=s.strip().lower()
    return len(t)<4 or t in TRIVIAL

def _is_derm_relevant(s:str)->bool:
    t=s.lower()
    return any(k in t for k in DERM_HINT_GOOD)

def _too_generic(s:str)->bool:
    t=s.lower()
    hits=sum(1 for k in GENERIC_BAD if k in t)
    return hits>=2 and not _is_derm_relevant(s)

def _fmt_sentence(s:str)->str:
    s=s.strip()
    s=re.sub(r"\s+"," ",s)
    s=re.sub(r"[ \t]*([.;,])+$","",s).strip()
    if s and not s[0].isupper(): s=s[0].upper()+s[1:]
    if s and s[-1] not in ".!?": s+="."
    return s

def _largest_red_roi(img:Image.Image)->Optional[tuple[int,int,int,int]]:
    arr=np.asarray(img.convert("RGB")); h,w,_=arr.shape
    if h*w<20000: return None
    r,g,b=arr[...,0].astype(np.float32),arr[...,1].astype(np.float32),arr[...,2].astype(np.float32)
    score=r-(g+b)/2.0
    thr=max(20.0, np.percentile(score,95))
    mask=score>thr
    if mask.sum()<200: return None
    ys,xs=np.where(mask); y1,y2=ys.min(),ys.max(); x1,x2=xs.min(),xs.max()
    py,px=int(0.08*(y2-y1+1)), int(0.08*(x2-x1+1))
    y1=max(0,y1-py); y2=min(h-1,y2+py); x1=max(0,x1-px); x2=min(w-1,x2+px)
    if (y2-y1)*(x2-x1)<0.01*h*w: return None
    return (x1,y1,x2+1,y2+1)

def _crop_lesion(img:Image.Image)->Image.Image:
    box=_largest_red_roi(img)
    return img.crop(box) if box else img

def _vqa_pipe():
    global _vqa
    if _vqa is None:
        from transformers import pipeline
        _vqa=pipeline("visual-question-answering", model=VQA_MODEL_ID, framework="pt", device=-1)
    return _vqa

def _cap_pipe():
    global _cap1
    if _cap1 is None:
        from transformers import pipeline
        _cap1=pipeline("image-to-text", model=CAP_MODEL_ID1, framework="pt", device=-1)
    return _cap1

def caption_image(img:Image.Image)->Optional[str]:
    """Kthen një fjali derm-focused pa prefikse; ose None nëse s’ka diçka të dobishme."""
    roi=_crop_lesion(img)


    try:
        qa=_vqa_pipe()
        q=("In one concise, non-diagnostic clinical sentence, describe the visible skin lesion: "
           "location (if visible), color (e.g., erythema), scaling/crusting, borders (well-demarcated vs ill-defined), "
           "and pattern/distribution.")
        ans=qa({"image":roi,"question":q})[0]["answer"].strip()
        if not _looks_trivial(ans) and (_is_derm_relevant(ans) or len(ans)>=20):
            return _fmt_sentence(ans)
    except Exception:
        pass


    try:
        cap=_cap_pipe()
        out=cap(roi, max_new_tokens=MAX_NEW, num_beams=3)
        c= (out[0].get("generated_text") or "").strip()
        if c and not _too_generic(c): return _fmt_sentence(c)
        out=cap(img, max_new_tokens=MAX_NEW, num_beams=3)
        c= (out[0].get("generated_text") or "").strip()
        if c and not _too_generic(c): return _fmt_sentence(c)
    except Exception:
        pass

    return None
