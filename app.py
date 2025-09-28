from __future__ import annotations
from typing import Optional
import logging
from flask import Flask, request, jsonify, render_template
from PIL import Image
from derm_embed import predict_skin_condition
from medgemma_infer import analyze_symptoms

app = Flask(__name__, static_folder="static", template_folder="templates")
app.logger.setLevel(logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return render_template("detect.html")

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

        # (1) Only picture
        # (2) Only text
        # (3) Both
        label = None
        score = None
        if img is not None:
            try:
                label, score = predict_skin_condition(img)
                score = float(score)
            except Exception as e:
                app.logger.exception("Image model error")
                return jsonify({"message": f"Image model error: {e}"}), 500

        explanation = analyze_symptoms(img, symptom_text) if has_text else None

        return jsonify({
            "disease": label,
            "accuracy": score,
            "symptom_analysis": explanation
        }), 200

    except Exception as e:
        app.logger.exception("Unhandled server error")
        return jsonify({"message": f"Unhandled server error: {e}"}), 500

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5050, debug=True)

