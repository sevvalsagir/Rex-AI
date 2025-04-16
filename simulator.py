import requests
import random
import time

URL = "http://127.0.0.1:5000/track"

ATTACK_UAS = ["curl/7.64.1", "Googlebot", "sqlmap/1.5", "CustomScanner/1.0", "BOT/1.0"]
NORMAL_UAS = ["Mozilla/5.0", "Chrome/119.0", "Safari/13.1.2", "Edge/95.0"]

URLS = {
    "normal": ["/home", "/about", "/products", "/api/info"],
    "sqli": ["/product?id=1' OR '1'='1", "/search?q=admin'--", "/user?id=1 OR 1=1"],
    "brute": ["/login", "/login", "/login"],
    "portscan": [f"/port{random.randint(1000,9999)}" for _ in range(10)],
    "ddos": ["/track", "/track", "/track"]
}

traffic_plan = []

# 🚨 DDoS
for _ in range(8):
    traffic_plan.append({
        "ip": f"198.51.{random.randint(1,254)}.{random.randint(1,254)}",
        "user_agent": random.choice(ATTACK_UAS),
        "urls": URLS["ddos"],
        "count": 30,
        "delay": 0.03,
        "is_attack": True,
        "status": 429
    })

# 🚨 Brute-force
for _ in range(5):
    traffic_plan.append({
        "ip": f"203.0.113.{random.randint(1,254)}",
        "user_agent": "Mozilla/5.0",
        "urls": URLS["brute"],
        "count": 10,
        "delay": 0.3,
        "is_attack": True,
        "status": 401
    })

# 🚨 SQLi
for _ in range(5):
    traffic_plan.append({
        "ip": f"192.0.2.{random.randint(1,254)}",
        "user_agent": "sqlmap/1.4.3",
        "urls": URLS["sqli"],
        "count": 10,
        "delay": 0.2,
        "is_attack": True,
        "status": 500
    })

# 🚨 Port scan
for _ in range(4):
    traffic_plan.append({
        "ip": f"10.0.0.{random.randint(1,254)}",
        "user_agent": "scanner-bot",
        "urls": URLS["portscan"],
        "count": 10,
        "delay": 0.15,
        "is_attack": True,
        "status": 404
    })

# ❌ Other
for _ in range(3):
    traffic_plan.append({
        "ip": f"172.16.{random.randint(0, 31)}.{random.randint(1, 254)}",
        "user_agent": "???",
        "urls": ["/unknown", "/⚠️", "/bad/request"],
        "count": 7,
        "delay": 0.5,
        "is_attack": True,
        "status": 520
    })

# ✅ Normal
for _ in range(10):
    traffic_plan.append({
        "ip": f"185.60.{random.randint(10,200)}.{random.randint(1,254)}",
        "user_agent": random.choice(NORMAL_UAS),
        "urls": URLS["normal"],
        "count": random.randint(3, 6),
        "delay": 0.6,
        "is_attack": False,
        "status": 200
    })

# ✅ Yanıltıcı (Normal görünümlü ama saldırgan)
for _ in range(5):
    traffic_plan.append({
        "ip": f"203.100.{random.randint(1,254)}.{random.randint(1,254)}",
        "user_agent": "Mozilla/5.0",
        "urls": URLS["ddos"],
        "count": 20,
        "delay": 0.05,
        "is_attack": True,
        "status": 200
    })

# ▶️ MAIN
if __name__ == "__main__":
    random.shuffle(traffic_plan)

    for plan in traffic_plan:
        for _ in range(plan["count"]):
            chosen_url = random.choice(plan["urls"])
            headers = {
                "User-Agent": plan["user_agent"],
                "X-Forwarded-For": plan["ip"],
                "X-Simulated-Status": str(plan["status"]),
                "X-Requested-URL": chosen_url
            }
            try:
                r = requests.get(URL, headers=headers, timeout=2)
                tag = "🚨 ATTACK" if plan["is_attack"] else "✅ NORMAL"
                print(f"{tag} | {plan['ip']} | {plan['user_agent']} | {plan['status']} | {chosen_url}")
                time.sleep(plan["delay"])
            except Exception as e:
                print("❌ Error:", e)
