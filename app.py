from __future__ import annotations
from typing import Optional
import logging
from flask import Flask, request, jsonify, render_template
from PIL import Image
from derm_foundation import predict_skin_condition, derm_embedding
from tiny_llama  import analyze_symptoms  # pranon img: Optional[Image.Image]

app = Flask(__name__, static_folder="static", template_folder="templates")
app.logger.setLevel(logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return render_template("detect.html")

@app.get("/health")
def health():
    return {"ok": True}, 200

@app.route("/detect", methods=["POST"])
def detect():
    try:
        app.logger.info("HIT /detect")
        file = request.files.get("file")
        symptom_text = (request.form.get("symptom") or "").strip()

        has_file = file is not None and file.filename != ""
        has_text = len(symptom_text) > 0

        if not has_file and not has_text:
            return jsonify({"message": "Provide an image or write symptoms."}), 400

        img: Optional[Image.Image] = None
        if has_file:
            try:
                img = Image.open(file.stream).convert("RGB")
            except Exception as e:
                app.logger.exception("Could not read image")
                return jsonify({"message": f"Could not read image: {e}"}), 400

        # (1) Vetëm foto  → klasifikim + embedding
        # (2) Vetëm tekst → analizë tekstuale (img=None)
        # (3) Të dyja     → klasifikim + embedding + analizë
        label = None
        score = None
        embedding = None

        if img is not None:
            try:
                label, score = predict_skin_condition(img)
                score = float(score)
            except Exception as e:
                app.logger.exception("Image model error")
                return jsonify({"message": f"Image model error: {e}"}), 500

            # Nxjerr embedding nga Derm Foundation
            try:
                embedding = derm_embedding(img).astype(float).tolist()
            except Exception as e:
                app.logger.warning("Derm embedding failed: %s", e)
                embedding = None

        explanation = analyze_symptoms(img, symptom_text) if has_text else None

        return jsonify({
            "disease": label,          # None kur s’ka foto
            "accuracy": score,         # None kur s’ka foto
            "embedding": embedding,    # list[float] ose None (mund të jetë e gjatë)
            "symptom_analysis": explanation  # None kur s’ka tekst
        }), 200

    except Exception as e:
        app.logger.exception("Unhandled server error")
        return jsonify({"message": f"Unhandled server error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5051, debug=True, use_reloader=False)


