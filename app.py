from __future__ import annotations
from typing import Optional
import logging, re
from flask import Flask, request, jsonify, render_template
from PIL import Image
from image import caption_image

try:
    from text import analyze_symptoms
except Exception:
    analyze_symptoms = None

app = Flask(__name__, static_folder="static", template_folder="templates")
app.logger.setLevel(logging.INFO)

def _clean_clause(s:str)->str:
    if not s: return ""
    s=s.strip()
    s=re.sub(r"(?i)\b(image|non-diagnostic|derm[- ]?focused).*?:\s*","",s).strip() 
    s=re.sub(r"[ \t]*([.;,])+$","",s).strip()
    if s and not s[0].isupper(): s=s[0].upper()+s[1:]
    if s and s[-1] not in ".!?": s+="."
    return s

def _combine_paragraph(photo_txt:Optional[str], symptom_txt:Optional[str])->Optional[str]:
    p=_clean_clause(photo_txt) if photo_txt else ""
    t=_clean_clause(symptom_txt) if symptom_txt else ""
    if p and t: return f"{p} {t}" 
    return p or t or None

@app.route("/", methods=["GET"])
def index(): return render_template("detect.html")

@app.get("/health")
def health(): return {"ok": True}, 200

@app.route("/detect", methods=["POST"])
def detect():
    try:
        file = request.files.get("file")
        symptom_text = (request.form.get("symptom") or "").strip()
        has_file = bool(file and file.filename)
        has_text = bool(symptom_text)
        if not has_file and not has_text:
            return jsonify({"message":"Provide an image or write symptoms."}), 400

        img: Optional[Image.Image] = None
        if has_file:
            try:
                img = Image.open(file.stream).convert("RGB")
            except Exception as e:
                app.logger.exception("Could not read image")
                return jsonify({"message": f"Could not read image: {e}"}), 400

        photo_sentence = None
        if img is not None:
            try:
                photo_sentence = caption_image(img)
            except Exception as e:
                app.logger.exception("Caption model failed")
                photo_sentence = None

        text_sentence = None
        if has_text:
            if analyze_symptoms:
                try:
                    text_sentence = analyze_symptoms(img, symptom_text) or ""
                except Exception as e:
                    app.logger.exception("Text analysis failed")
                    text_sentence = f"User-reported symptoms: {symptom_text}"
            else:
                text_sentence = f"User-reported symptoms: {symptom_text}"

        explanation = _combine_paragraph(photo_sentence, text_sentence)

        return jsonify({
            "disease": None,
            "accuracy": None,
            "symptom_analysis": explanation
        }), 200
    except Exception as e:
        app.logger.exception("Unhandled server error")
        return jsonify({"message": f"Unhandled server error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5051, debug=True, use_reloader=False)
