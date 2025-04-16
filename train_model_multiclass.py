# train_model_multiclass.py

import pandas as pd
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import re

# Dosya yolu
CSV_FILE = "live_log.csv"
MODEL_OUT = "model/rex_multiclass_model.pkl"

# 1. Veriyi oku
df = pd.read_csv(CSV_FILE)

# 2. Etiketsiz kayıtları at
df = df[df["label"].notna()]
df = df[df["label"] != -1]

# 3. Giriş özelliklerini oluştur
def is_bot_ua(ua):
    if isinstance(ua, str):
        return int(any(x in ua.lower() for x in ["curl", "bot", "scanner", "sqlmap"]))
    return 0

# Giriş özelliklerini oluştur
df["error_rate"] = df["status_code"].apply(lambda x: 1 if int(x) >= 400 else 0)
df["bot_like_ua"] = df["user_agent"].apply(is_bot_ua)

# Yeni özellikler
df["requests_per_10s"] = 5  # dummy veri, gerçek sistemde yok şu an
df["unique_urls"] = 3       # dummy
df["burst_ratio"] = 0.5     # dummy

# Özellik listesi genişletildi
features = [
    "requests_per_10s",
    "status_code",
    "unique_urls",
    "error_rate",
    "burst_ratio",
    "bot_like_ua"
]


X = df[features]
y = df["label"]

# 4. Train/test ayır
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 5. Modeli eğit
clf = RandomForestClassifier(n_estimators=150, max_depth=10, random_state=42)
clf.fit(X_train, y_train)

# 6. Performans raporu
y_pred = clf.predict(X_test)
print("📊 Classification Report:")
print(classification_report(y_test, y_pred))

# 7. Kaydet
joblib.dump(clf, MODEL_OUT)
print(f"✅ Model kaydedildi: {MODEL_OUT}")
