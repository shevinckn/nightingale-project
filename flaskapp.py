from flask import Flask, request, jsonify
import joblib
import numpy as np
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Tillåter frontend att anropa API:t

model = joblib.load("lightgbm_model.pkl")
encoder = joblib.load("label_encoder.pkl")

@app.route("/api/predict", methods=["POST"])
def predict():
    data = request.get_json()

    try:
        features = [
            float(data["ESV"]),
            float(data["EDV"]),
            float(data["FrameHeight"]),
            float(data["FrameWidth"]),
            float(data["FPS"]),
            float(data["NumberOfFrames"]),
        ]
        prediction = model.predict([features])[0]
        label = encoder.inverse_transform([prediction])[0]
        return jsonify({"prediction": label})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    app.run(debug=True)
