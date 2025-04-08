import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib
import os

# Simulate dataset: Normal and DDoS
def generate_data(samples=1000):
    np.random.seed(42)
    data = []

    # Normal traffic
    for _ in range(samples):
        ip = f"192.168.1.{np.random.randint(1, 100)}"
        rate = np.random.poisson(2)
        status = np.random.choice([200, 302])
        data.append([ip, rate, status, 0])  # 0 = normal

    # DDoS traffic
    for _ in range(samples):
        ip = f"10.0.0.{np.random.randint(1, 10)}"
        rate = np.random.poisson(20)
        status = np.random.choice([403, 429, 500])
        data.append([ip, rate, status, 1])  # 1 = attack

    df = pd.DataFrame(data, columns=["source_ip", "requests_per_10s", "status_code", "label"])
    return df

df = generate_data()
X = df[["requests_per_10s", "status_code"]]
y = df["label"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier()
model.fit(X_train, y_train)

print("\n📋 Model Evaluation:\n")
print(classification_report(y_test, model.predict(X_test)))

# Save the model
os.makedirs("model", exist_ok=True)
joblib.dump(model, "model/rex_model.pkl")
print("\n✅ Model saved to 'model/rex_model.pkl'")
