from flask import Flask, request, jsonify
import joblib
import numpy as np
import pandas as pd

app = Flask(__name__)

# Ladda modellen och encodern
model = joblib.load('lightgbm_model.pkl')
encoder = joblib.load('label_encoder.pkl')

# Lägg till en funktion för att få AI-prediktion
@app.route('/api/ai-answer', methods=['POST'])
def get_ai_answer():
    data = request.json

    try:
        # Extrahera features i rätt ordning
        features = [
            data["ESV"],
            data["EDV"],
            data["FrameHeight"],
            data["FrameWidth"],
            data["FPS"],
            data["NumberOfFrames"]
        ]
    except KeyError as e:
        return jsonify({'error': f'Missing feature: {e}'}), 400

    try:
        # Gör prediktion
        prediction_numeric = model.predict([features])[0]  # prediktionen som siffra
        prediction_label = encoder.inverse_transform([prediction_numeric])[0]  # konvertera till textetikett
        return jsonify({'answer': prediction_label})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Lägg till en funktion för att hämta frågor och metadata
@app.route('/api/questions', methods=['GET'])
def get_questions():
    df = pd.read_csv("FileList.csv")
    questions = []

    for _, row in df.iterrows():
        ef_label = row['EF']
        question = {
            "question": "Hur bedömer du denna EF-video?",
            "videoUrl": f"static/videos/{row['FileName']}",  # Video URL
            "answers": ["Normal", "Abnormal", "Reducerat"],
            "correct": ef_label,  # Antag att 'EF' är korrekt svar
            "metadata": {
                "ESV": row["ESV"],
                "EDV": row["EDV"],
                "FrameHeight": row["FrameHeight"],
                "FrameWidth": row["FrameWidth"],
                "FPS": row["FPS"],
                "NumberOfFrames": row["NumberOfFrames"]
            },
            "isVideo": True,
            "difficulty": "medium"
        }
        questions.append(question)

    return jsonify(questions)


if __name__ == '__main__':
    app.run(debug=True)
