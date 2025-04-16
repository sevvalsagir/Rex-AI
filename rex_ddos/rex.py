import pandas as pd
from collections import Counter

# CSV'den veriyi oku ve zaman sütununu dönüştür
df = pd.read_csv("traffic_log.csv")
df['timestamp'] = pd.to_datetime(df['timestamp'])

print("📊 Trafik verisi yüklendi.")

# IP başına toplam istek sayısı
ip_counts = Counter(df["source_ip"])
print("\n🔍 IP Başına İstek Sayıları:")
for ip, count in ip_counts.items():
    print(f"  {ip} → {count} istek")

# Basit eşik analizi
threshold = 5
print("\n🚨 Şüpheli IP'ler (Toplam Eşik):")
for ip, count in ip_counts.items():
    if count > threshold:
        print(f"  ⚠️ {ip} şüpheli! ({count} istek)")

# 🕒 Zaman bazlı analiz: her dakika için IP başına istek sayısı
df['minute'] = df['timestamp'].dt.floor('min')
grouped = df.groupby(['minute', 'source_ip']).size().reset_index(name='count')

print("\n⏱️ Dakika Bazlı Trafik:")
for _, row in grouped.iterrows():
    print(f"  {row['minute']} → {row['source_ip']} → {row['count']} istek")

# Ani artış tespiti: Eğer bir dakikada 4'ten fazla istek varsa
print("\n⚠️ Anormal Trafik Tespiti (Dakika Bazlı):")
for _, row in grouped.iterrows():
    if row['count'] > 4:
        print(f"  🚨 {row['source_ip']} → {row['minute']} → {row['count']} istek (ani artış!)")
