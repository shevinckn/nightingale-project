from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import pandas as pd
import joblib
import os
import csv
from datetime import datetime

app = Flask(__name__, static_folder="dist", static_url_path="")
CORS(app)

# Ladda ML-modell och encoder
model = joblib.load("lightgbm_model.pkl")
encoder = joblib.load("label_encoder.pkl")

RESULTS_FILE_CSV = "results.csv"

# === Funktioner ===

def write_results_to_csv(results):
    try:
        file_exists = os.path.isfile(RESULTS_FILE_CSV)
        with open(RESULTS_FILE_CSV, mode='a', newline='') as file:
            fieldnames = ['userID', 'score', 'ai_score', 'total', 'timestamp']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(results)
        print("Result saved:", results)
    except Exception as e:
        print("Error saving results to CSV:", e)

def ef_label(ef):
    ef = float(ef)
    if ef >= 55:
        return "Normal"
    elif 40 <= ef < 55:
        return "Reducerad"
    else:
        return "Abnormal"

# === ROUTES ===

@app.route("/api/questions", methods=["GET"])
def get_questions():
    try:
        # Läs in data från CSV med hjärtdata
        df = pd.read_csv("FileList.csv")
        df = df[pd.to_numeric(df["EF"], errors="coerce").notnull()]
        sampled = df.sample(n=min(15, len(df)))

        questions = []
        for _, row in sampled.iterrows():
            filename = f"{row['FileName']}.mp4"
            video_url = f"http://127.0.0.1:5000/videos/{filename}"
            questions.append({
                "question": "Vad är det mest sannolika EF-värdet för detta hjärta?",
                "answers": ["Normal", "Reducerad", "Abnormal"],
                "correct": ef_label(row["EF"]),
                "videoUrl": video_url,
                "difficulty": "medium",
                "metadata": {
                    "ESV": row["ESV"],
                    "EDV": row["EDV"],
                    "FrameHeight": row["FrameHeight"],
                    "FrameWidth": row["FrameWidth"],
                    "FPS": row["FPS"],
                    "NumberOfFrames": row["NumberOfFrames"]
                }
            })
        return jsonify(questions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/videos/<path:filename>")
def serve_video(filename):
    video_dir = os.path.join(os.path.dirname(__file__), "mp4")
    return send_from_directory(video_dir, filename)

@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()
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

@app.route("/api/ai-answer", methods=["POST"])
def ai_answer():
    try:
        data = request.get_json()
        metadata = data.get("metadata", {})
        features = [
            float(metadata.get("ESV", 0)),
            float(metadata.get("EDV", 0)),
            float(metadata.get("FrameHeight", 0)),
            float(metadata.get("FrameWidth", 0)),
            float(metadata.get("FPS", 0)),
            float(metadata.get("NumberOfFrames", 0)),
        ]
        prediction = model.predict([features])[0]
        label = encoder.inverse_transform([prediction])[0]

        # Generera en hint baserat på AI:s bedömning
        if label == "Normal":
            hint = "Hjärtat verkar vara friskt, men fortsätt vara uppmärksam på andra tecken på hjärtproblem."
        elif label == "Reducerad":
            hint = "Hjärtat har reducerad funktion, vilket kan vara ett tecken på hjärtsvikt eller andra problem."
        else:
            hint = "Abnormt EF-värde, vilket kan indikera allvarligare hjärtproblem. Vänligen kontakta läkare."

        return jsonify({"answer": label, "hint": hint})
    except Exception as e:
        print("Error in /api/ai-answer:", e)
        return jsonify({"answer": "Normal", "hint": "AI kunde inte ge en hint."})  # fallback

@app.route("/api/submit_results", methods=["POST"])
def submit_results():
    try:
        data = request.get_json()
        print("Received result submission:", data)

        result = {
            'userID': data.get("userID", "unknown"),
            'score': data.get("score"),
            'ai_score': data.get("ai_score"),
            'total': data.get("total"),
            'timestamp': data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        if None in result.values() or "" in result.values():
            return jsonify({"error": "Missing required fields"}), 400

        write_results_to_csv(result)
        return jsonify({"status": "saved"}), 200
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

@app.route("/")
def index():
    return app.send_static_file("index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return app.send_static_file(path)

if __name__ == "__main__":
    app.run(debug=True)
