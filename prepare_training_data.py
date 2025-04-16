import pandas as pd
from collections import defaultdict
from datetime import datetime

# Okuma
df = pd.read_csv("live_log.csv")
df = df[df["label"] != -1]

# IP bazlı loglar
ip_request_log = defaultdict(list)
ip_url_log = defaultdict(set)
ip_status_log = defaultdict(list)

feature_rows = []

for _, row in df.iterrows():
    try:
        timestamp = pd.to_datetime(row["timestamp"])
        ip = row["source_ip"]
        url = row["url"]
        status = int(row["status_code"])
        user_agent = str(row["user_agent"]).lower()
        label = int(row["label"])

        ip_request_log[ip].append(timestamp)
        ip_url_log[ip].add(url)
        ip_status_log[ip].append(status)

        now = timestamp
        recent = [t for t in ip_request_log[ip] if (now - t).total_seconds() < 10]
        burst_ratio = round(len([t for t in recent if (now - t).total_seconds() < 2]) / len(recent), 2) if recent else 0
        error_count = len([code for code in ip_status_log[ip] if code >= 400])
        total_count = len(ip_status_log[ip])
        error_rate = round(error_count / total_count, 2) if total_count > 0 else 0
        is_bot_ua = 1 if any(x in user_agent for x in ["curl", "bot", "scanner", "sqlmap"]) else 0
        unique_urls = len(ip_url_log[ip])

        feature_rows.append({
            "requests_per_10s": len(recent),
            "status_code": status,
            "unique_urls": unique_urls,
            "error_rate": error_rate,
            "burst_ratio": burst_ratio,
            "is_bot": is_bot_ua,
            "label": label
        })
    except Exception as e:
        print(f"Satır atlandı: {e}")

# Kaydet
final_df = pd.DataFrame(feature_rows)
final_df.to_csv("training_dataset.csv", index=False)
print("✅ Eğitim verisi hazır: training_dataset.csv")
