import pandas as pd
from collections import defaultdict
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# 🔄 Veriyi oku
LOG_FILE = "live_log.csv"
MODEL_PATH = "model/rex_model.pkl"

if not os.path.exists(LOG_FILE):
    print("❌ live_log.csv bulunamadı.")
    exit()

df = pd.read_csv(LOG_FILE)

# ❗ Sadece etiketlenmiş veriyi al
df = df[df["label"] != -1]

if df.empty:
    print("❌ Etiketli veri bulunamadı. Lütfen /label panelinden etiket ekleyin.")
    exit()

# 🧠 IP bazlı log geçmişi oluştur
ip_request_log = defaultdict(list)
ip_url_log = defaultdict(set)
ip_status_log = defaultdict(list)

features = []
labels = []

for _, row in df.iterrows():
    try:
        timestamp = pd.to_datetime(row["timestamp"])
        ip = row["source_ip"]
        url = row["url"]
        user_agent = str(row["user_agent"]).lower()
        status_code = int(row["status_code"])
        label = int(row["label"])

        ip_request_log[ip].append(timestamp)
        ip_url_log[ip].add(url)
        ip_status_log[ip].append(status_code)

        now = timestamp
        recent_requests = [t for t in ip_request_log[ip] if (now - t).total_seconds() < 10]
        burst_ratio = round(len([t for t in recent_requests if (now - t).total_seconds() < 2]) / len(recent_requests), 2) if recent_requests else 0
        error_count = len([code for code in ip_status_log[ip] if code >= 400])
        total_count = len(ip_status_log[ip])
        error_rate = round(error_count / total_count, 2) if total_count > 0 else 0
        is_bot_ua = 1 if any(x in user_agent for x in ["curl", "bot", "scanner", "sqlmap"]) else 0
        unique_urls = len(ip_url_log[ip])

        feature_row = [
            len(recent_requests),
            status_code,
            unique_urls,
            error_rate,
            burst_ratio,
            is_bot_ua
        ]

        features.append(feature_row)
        labels.append(label)

    except Exception as e:
        print(f"⚠️ Satır atlandı: {e}")
        continue

# 🧪 Eğitim ve test verisine ayır
X = pd.DataFrame(features, columns=[
    "requests_per_10s",
    "status_code",
    "unique_urls",
    "error_rate",
    "burst_ratio",
    "is_bot"
])
y = pd.Series(labels)

print(f"📊 Veri boyutu: {X.shape}, Sınıf dağılımı: {y.value_counts().to_dict()}")

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 🎯 Model eğitimi
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# 📈 Performans çıktısı
y_pred = model.predict(X_test)
print("\n🧾 Model Performansı:\n")
print(classification_report(y_test, y_pred))

# 💾 Kaydet
os.makedirs("model", exist_ok=True)
joblib.dump(model, MODEL_PATH)
print(f"\n✅ Model başarıyla kaydedildi → {MODEL_PATH}")
