import pandas as pd
import random
from datetime import datetime, timedelta

# Sınıf etiketleri:
# 0 → Normal
# 1 → DDoS
# 2 → Brute-force
# 3 → Port Scan
# 4 → SQLi
# 5 → Other

def generate_log(label):
    now = datetime.now()
    base_ip = f"192.168.{random.randint(0, 255)}.{random.randint(1, 254)}"

    if label == 0:  # ✅ Normal
        return {
            "timestamp": now,
            "source_ip": base_ip,
            "url": random.choice(["/home", "/about", "/product", "/contact"]),
            "user_agent": "Mozilla/5.0",
            "status_code": 200,
            "label": label
        }

    elif label == 1:  # 🚨 DDoS
        return {
            "timestamp": now,
            "source_ip": base_ip,
            "url": "/track",
            "user_agent": "curl/7.58.0",
            "status_code": random.choice([429, 503, 500]),
            "label": label
        }

    elif label == 2:  # 🔓 Brute-force
        return {
            "timestamp": now,
            "source_ip": base_ip,
            "url": "/login",
            "user_agent": "Mozilla/5.0",
            "status_code": 401,
            "label": label
        }

    elif label == 3:  # 🕵️ Port Scan
        return {
            "timestamp": now,
            "source_ip": base_ip,
            "url": f"/port{random.randint(1000, 9999)}",
            "user_agent": "scanner-bot",
            "status_code": 404,
            "label": label
        }

    elif label == 4:  # 🧬 SQLi
        return {
            "timestamp": now,
            "source_ip": base_ip,
            "url": "/product?id=1' OR '1'='1",
            "user_agent": "sqlmap/1.3.12",
            "status_code": 500,
            "label": label
        }

    elif label == 5:  # ❓ Other
        return {
            "timestamp": now,
            "source_ip": base_ip,
            "url": "/weird_path/⚠️",
            "user_agent": "unknown-agent",
            "status_code": random.choice([418, 520, 999]),
            "label": label
        }

# 🔁 Her sınıftan eşit sayıda üret
sample_count_per_class = 200
all_rows = []

for label in range(6):
    for _ in range(sample_count_per_class):
        all_rows.append(generate_log(label))

df = pd.DataFrame(all_rows)
df.to_csv("live_log.csv", index=False)
print("✅ Sahte loglar üretildi → live_log.csv (6 sınıf, dengeli)")
