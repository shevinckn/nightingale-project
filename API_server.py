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

# Dummy AI-analys – ersätt med riktig logik om du vill
def process_data(data):
    return "Normal"

# Funktion för att skriva resultat till CSV
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

# === ROUTES ===

@app.route("/api/questions", methods=["GET"])
def get_questions():
    try:
        df = pd.read_csv("FileList.csv")
        df = df[pd.to_numeric(df["EF"], errors="coerce").notnull()]
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
            questions.append({
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
    data = request.get_json()
    result = process_data(data)
    return jsonify({'answer': result})

@app.route("/api/submit_results", methods=["POST"])
def submit_results():
    try:
        data = request.get_json()
        print("Received result submission:", data)

        # Extrahera fält
        result = {
            'userID': data.get("userID", "unknown"),
            'score': data.get("score"),
            'ai_score': data.get("ai_score"),
            'total': data.get("total"),
            'timestamp': data.get("timestamp") or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        # Kontrollera obligatoriska fält
        if None in result.values() or "" in result.values():
            return jsonify({"error": "Missing required fields"}), 400

        # Spara till CSV
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
