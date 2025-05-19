import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder
import joblib
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Läs in data
df = pd.read_csv("FileList.csv")

# 2. Kategorisera EF
def ef_category(ef):
    if ef > 50:
        return "Normal"
    elif ef > 40:
        return "Abnormal"
    else:
        return "Reducerat"

df["EF_label"] = df["EF"].apply(ef_category)

# 3. Förbered features och labels
X = df[["ESV", "EDV", "FrameHeight", "FrameWidth", "FPS", "NumberOfFrames"]]
y = df["EF_label"]

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

# 4. Dela upp i träning/test
X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

# 5. Träna modell
model = lgb.LGBMClassifier()
model.fit(X_train, y_train)

# 6. Förutsägelser
y_pred = model.predict(X_test)

# 7. Klassificeringsrapport
print("\nKlassificeringsrapport:\n")
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

# 8. Confusion Matrix
cm = confusion_matrix(y_test, y_pred)
plt.figure(figsize=(6, 5))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
            xticklabels=encoder.classes_,
            yticklabels=encoder.classes_)
plt.xlabel("Prediktion")
plt.ylabel("Verklig klass")
plt.title("Confusion Matrix")
plt.show()

# 9. Spara modell om du vill
joblib.dump(model, "lightgbm_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")
