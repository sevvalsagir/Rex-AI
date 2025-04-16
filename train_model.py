import pandas as pd
import numpy as np
import random

def generate_simulated_data(samples=2000):
    np.random.seed(42)
    random.seed(42)
    data = []

    for _ in range(samples):
        # 🎯 60% Normal - 30% Attack - 10% Ambiguous
        prob = np.random.rand()
        if prob < 0.6:
            label = 0  # normal
        elif prob < 0.9:
            label = 1  # attack
        else:
            label = 2  # ambiguous

        if label == 0:
            # Normal users
            ip = f"192.168.{random.randint(0, 10)}.{random.randint(1, 254)}"
            user_agent = random.choice(["Mozilla/5.0", "Chrome/119.0", "Safari/13.1.2", "Edge/95.0"])
            status_code = np.random.choice([200, 302, 304], p=[0.8, 0.15, 0.05])
            requests_per_10s = np.random.poisson(2)
            unique_urls_per_ip = np.random.randint(3, 10)
            error_rate = round(np.random.uniform(0, 0.1), 2)
            burst_ratio = round(np.random.uniform(0.05, 0.3), 2)
            is_bot_user_agent = 0

        elif label == 1:
            # Diverse attack types
            attack_type = random.choice(["burst", "botlike", "stealth", "mimic"])
            ip = f"10.0.{random.randint(0, 10)}.{random.randint(1, 254)}"
            if attack_type == "burst":
                user_agent = random.choice(["sqlmap/1.5", "curl/7.64.1", "BOT/1.0"])
                requests_per_10s = np.random.randint(20, 60)
                burst_ratio = round(np.random.uniform(0.8, 1.0), 2)
                error_rate = round(np.random.uniform(0.3, 1.0), 2)
                unique_urls_per_ip = np.random.randint(1, 3)
                status_code = np.random.choice([403, 429, 500], p=[0.4, 0.4, 0.2])
            elif attack_type == "botlike":
                user_agent = random.choice(["Googlebot", "CustomScanner/1.0"])
                requests_per_10s = np.random.randint(10, 40)
                burst_ratio = round(np.random.uniform(0.6, 0.9), 2)
                error_rate = round(np.random.uniform(0.4, 0.9), 2)
                unique_urls_per_ip = np.random.randint(1, 2)
                status_code = np.random.choice([403, 429, 200])
            elif attack_type == "stealth":
                user_agent = "Mozilla/5.0"
                requests_per_10s = np.random.randint(3, 5)
                burst_ratio = round(np.random.uniform(0.4, 0.6), 2)
                error_rate = round(np.random.uniform(0.2, 0.6), 2)
                unique_urls_per_ip = 1
                status_code = 200
            elif attack_type == "mimic":
                user_agent = "Mozilla/5.0"
                requests_per_10s = np.random.randint(10, 20)
                burst_ratio = round(np.random.uniform(0.7, 0.9), 2)
                error_rate = round(np.random.uniform(0.1, 0.3), 2)
                unique_urls_per_ip = np.random.randint(1, 3)
                status_code = 200

            is_bot_user_agent = 1 if any(x in user_agent.lower() for x in ["curl", "bot", "sqlmap", "scanner"]) else 0

        else:
            # Ambiguous (gri) trafik
            ip = f"172.16.{random.randint(0, 10)}.{random.randint(1, 254)}"
            user_agent = random.choice(["Mozilla/5.0", "curl/7.64.1"])
            status_code = np.random.choice([200, 403, 429])
            requests_per_10s = np.random.randint(5, 15)
            unique_urls_per_ip = np.random.randint(1, 6)
            error_rate = round(np.random.uniform(0.1, 0.4), 2)
            burst_ratio = round(np.random.uniform(0.3, 0.7), 2)
            is_bot_user_agent = 1 if "curl" in user_agent.lower() else 0
            label = np.random.choice([0, 1])  # zorlaştırma: rastgele etiketle

        data.append([
            ip,
            requests_per_10s,
            status_code,
            unique_urls_per_ip,
            error_rate,
            burst_ratio,
            is_bot_user_agent,
            label
        ])

    df = pd.DataFrame(data, columns=[
        "source_ip",
        "requests_per_10s",
        "status_code",
        "unique_urls_per_ip",
        "error_rate",
        "burst_ratio",
        "is_bot_user_agent",
        "label"
    ])

    return df

if __name__ == "__main__":
    df = generate_simulated_data()
    print(df.head())  # isteğe bağlı: veri önizleme

    X = df.drop(columns=["source_ip", "label"])
    y = df["label"]

    from sklearn.ensemble import RandomForestClassifier
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)

    import joblib
    joblib.dump(model, "model/rex_model.pkl")
    print("✅ Model trained and saved to model/rex_model.pkl")
