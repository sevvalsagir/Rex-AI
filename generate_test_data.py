# generate_test_data.py

import pandas as pd
import random
from datetime import datetime, timedelta

CSV_FILE = "live_log.csv"

# Saldırı tipleri ve oranları
attack_types = {
    0: "✅ Normal",
    1: "🚨 DDoS",
    2: "🔓 Brute-force",
    3: "🕵️ Port Scan",
    4: "🧬 SQL Injection",
    5: "❓ Other"
}

user_agents = {
    0: "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    1: "curl/7.68.0",
    2: "sqlmap/1.5.1#stable",
    3: "Hydra/9.1",
    4: "Nmap/7.80",
    5: "Python-urllib/3.7"
}

# Test verisi üret
rows = []
now = datetime.now()

for i in range(30):
    label = random.randint(0, 5)
    ip = f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"
    status_code = random.choices([200, 403, 404, 500], weights=[5, 2, 2, 1])[0]
    url = random.choice(["/login", "/api/data", "/admin", "/search", "/"])
    user_agent = user_agents[random.randint(0, 5)]
    timestamp = now - timedelta(seconds=random.randint(0, 300))

    rows.append({
        "timestamp": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        "source_ip": ip,
        "url": url,
        "user_agent": user_agent,
        "status_code": status_code,
        "label": label
    })

df_new = pd.DataFrame(rows)

# Eğer dosya yoksa, başlıkla oluştur
try:
    df_old = pd.read_csv(CSV_FILE)
except FileNotFoundError:
    df_old = pd.DataFrame()

# Birleştir ve kaydet
df_combined = pd.concat([df_old, df_new], ignore_index=True)
df_combined.to_csv(CSV_FILE, index=False)

print(f"✅ {len(df_new)} adet örnek eklendi → {CSV_FILE}")
