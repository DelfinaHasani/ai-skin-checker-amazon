from __future__ import annotations
import logging
from flask import Flask, request, jsonify, render_template
from PIL import Image
from derm_embed import predict_skin_condition
from medgemma_infer import analyze_symptoms  # stub i lehtë (nuk shkarkon modele)

app = Flask(__name__, static_folder="static", template_folder="templates")
app.logger.setLevel(logging.INFO)

@app.route("/", methods=["GET"])
def index():
    return render_template("detect.html")

@app.route("/detect", methods=["POST"])
def detect():
    try:
        app.logger.info("HIT /detect")
        app.logger.info("FILES: %s", list(request.files.keys()))
        app.logger.info("FORM: %s", dict(request.form))

        file = request.files.get("file")
        if file is None or file.filename == "":
            return jsonify({"message": "No image file provided (form field 'file')."}), 400

        symptom_text = (request.form.get("symptom") or "").strip()

        try:
            img = Image.open(file.stream).convert("RGB")
        except Exception as e:
            app.logger.exception("Could not read image")
            return jsonify({"message": f"Could not read image: {e}"}), 400

        try:
            label, score = predict_skin_condition(img)
            score = float(score)
        except Exception as e:
            app.logger.exception("Image model error")
            return jsonify({"message": f"Image model error: {e}"}), 500

        explanation = analyze_symptoms(img, symptom_text) if symptom_text else None

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
