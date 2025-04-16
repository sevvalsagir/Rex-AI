import requests
import random
import time

URL = "http://127.0.0.1:5000/track"

ATTACK_UAS = ["curl/7.64.1", "Googlebot", "sqlmap/1.5", "CustomScanner/1.0", "BOT/1.0"]
NORMAL_UAS = ["Mozilla/5.0", "Chrome/119.0", "Safari/13.1.2", "Edge/95.0"]

traffic_plan = []

# 🔴 10 bot-like IP
for _ in range(10):
    traffic_plan.append({
        "ip": f"45.67.{random.randint(10, 200)}.{random.randint(1, 254)}",
        "user_agent": random.choice(ATTACK_UAS),
        "count": random.randint(15, 30),
        "delay": 0.05,
        "is_attack": True,
        "status": random.choice([403, 429, 500])
    })

# 🔴 5 stealth IP
for _ in range(5):
    traffic_plan.append({
         "ip": f"45.67.{random.randint(10, 200)}.{random.randint(1, 254)}",
        "user_agent": "Mozilla/5.0",
        "count": random.randint(6, 10),
        "delay": 0.7,
        "is_attack": True,
        "status": 200
    })

# 🔴 5 mimic IP
for _ in range(5):
    traffic_plan.append({
        "ip": f"45.67.{random.randint(10, 200)}.{random.randint(1, 254)}",
        "user_agent": "Chrome/119.0",
        "count": random.randint(10, 20),
        "delay": 0.1,
        "is_attack": True,
        "status": 200
    })

# 🟢 7 normal IP
for _ in range(7):
    traffic_plan.append({
        "ip": f"45.67.{random.randint(10, 200)}.{random.randint(1, 254)}",
        "user_agent": random.choice(NORMAL_UAS),
        "count": random.randint(1, 5),
        "delay": 0.5,
        "is_attack": False,
        "status": 200
    })

# ✅ MAIN BLOK
if __name__ == "__main__":
    random.shuffle(traffic_plan)

    for plan in traffic_plan:
        for _ in range(plan["count"]):
            headers = {
                "User-Agent": plan["user_agent"],
                "X-Forwarded-For": plan["ip"],
                "X-Simulated-Status": str(plan["status"])
            }
            try:
                r = requests.get(URL, headers=headers, timeout=2)
                tag = "🚨 ATTACK" if plan["is_attack"] else "✅ NORMAL"
                print(f"{tag} | {plan['ip']} | {plan['user_agent']} | {plan['status']}")
                time.sleep(plan["delay"])
            except Exception as e:
                print("❌ Error:", e)
                continue
