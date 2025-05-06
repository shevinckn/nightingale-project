import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
from sklearn.preprocessing import LabelEncoder
import joblib

df = pd.read_csv("FileList.csv")

def ef_category(ef):
    if ef > 50:
        return "Normal"
    elif ef > 40:
        return "Abnormal"
    else:
        return "Reducerat"

df["EF_label"] = df["EF"].apply(ef_category)

X = df[["ESV", "EDV", "FrameHeight", "FrameWidth", "FPS", "NumberOfFrames"]]
y = df["EF_label"]

encoder = LabelEncoder()
y_encoded = encoder.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

model = lgb.LGBMClassifier()
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=encoder.classes_))

joblib.dump(model, "lightgbm_model.pkl")
joblib.dump(encoder, "label_encoder.pkl")
