# train_model_multiclass.py
import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

def retrain_model(csv_path="live_log.csv", model_path="model/rex_model.pkl"):
    df = pd.read_csv(csv_path)

    if "label" not in df.columns:
        print("❌ Label sütunu bulunamadı.")
        return

    df = df[df["label"] >= 0]  # Sadece etiketlenmiş olanlar

    # Feature engineering
    df["error_rate"] = (df["status_code"] >= 400).astype(int)
    df["burst_ratio"] = 0.7  # Şimdilik sabit varsay
    df["is_bot_ua"] = df["user_agent"].str.contains("curl|bot|sqlmap|scanner", case=False).astype(int)
    df["unique_urls"] = 1

    features = df[["status_code", "unique_urls", "error_rate", "burst_ratio", "is_bot_ua"]]
    labels = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    model = RandomForestClassifier(n_estimators=150, class_weight="balanced", random_state=42)
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("🧾 Model Retrained – Performance:\n")
    print(classification_report(y_test, y_pred))

    joblib.dump(model, model_path)
    print(f"✅ Model kaydedildi: {model_path}")
