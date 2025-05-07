from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import joblib
import random
import os

app = Flask(__name__)
CORS(app)  # Tillåter anrop från frontend

# Ladda ML-modell och encoder (om du använder den för prediction)
model = joblib.load("lightgbm_model.pkl")
encoder = joblib.load("label_encoder.pkl")

# API: Skapa quizfrågor
@app.route("/api/questions", methods=["GET"])
def get_questions():
    try:
        df = pd.read_csv("FileList.csv")

        # Filtrera bort ogiltiga EF
        df = df[pd.to_numeric(df["EF"], errors="coerce").notnull()]

        # Välj slumpmässiga rader (max 15)
        sampled = df.sample(n=min(15, len(df)))

        def get_label_from_value(ef):
            ef = float(ef)
            if ef >= 55:
                return "Normal"
            elif 40 <= ef < 55:
                return "Reducerad"
            else:
                return "Abnormal"

        questions = []
        for _, row in sampled.iterrows():
            filename = f"{row['FileName']}.mp4"
            video_url = f"http://127.0.0.1:5000/videos/{filename}"
  # Detta pekar på route nedan

            question = {
                "question": "Vad är det mest sannolika EF-värdet för detta hjärta?",
                "answers": ["Normal", "Reducerad", "Abnormal"],
                "correct": get_label_from_value(row["EF"]),
                "videoUrl": video_url,
                "metadata": {
                    "ESV": row["ESV"],
                    "EDV": row["EDV"],
                    "FrameHeight": row["FrameHeight"],
                    "FrameWidth": row["FrameWidth"],
                    "FPS": row["FPS"],
                    "NumberOfFrames": row["NumberOfFrames"]
                }
            }
            questions.append(question)

        return jsonify(questions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API: Serve video från /mp4
@app.route("/videos/<path:filename>")
def serve_video(filename):
    return send_from_directory(r"C:\Users\shevi\Desktop\nightingale-project\mp4", filename)

# API: ML prediction (om du använder det)
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
