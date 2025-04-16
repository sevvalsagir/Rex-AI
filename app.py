from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import pandas as pd
import os
from collections import defaultdict, Counter
import joblib
import geoip2.database
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from attack_counter import register_attack, check_alarm, should_send_email
import yagmail
import config_email
from datetime import datetime


app = Flask(__name__)
socketio = SocketIO(app)

# Paths
LOG_FILE = "live_log.csv"
ATTACK_LOG_FILE = "attack_log.csv"
MODEL_FILE = "model/rex_model.pkl"

LABEL_MAP = {
    0: "✅ NORMAL",
    1: "🚨 DDoS",
    2: "🔓 Brute-force",
    3: "🕵️ Port Scan",
    4: "🧬 SQLi",
    5: "❓ Other"
}


# Load trained model
model = joblib.load(MODEL_FILE)

# Request history for feature extraction
ip_request_log = defaultdict(list)
ip_url_log = defaultdict(set)
ip_status_log = defaultdict(list)

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/track", methods=["GET"])
def track():
    ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    url = request.path
    user_agent = request.headers.get("User-Agent", "unknown")
    timestamp = datetime.now()
    status_code = int(request.headers.get("X-Simulated-Status", 200))

    ip_request_log[ip].append(timestamp)
    ip_url_log[ip].add(url)
    ip_status_log[ip].append(status_code)

    now = timestamp
    recent_requests = [t for t in ip_request_log[ip] if (now - t).seconds < 10]
    burst_ratio = round(len([t for t in recent_requests if (now - t).seconds < 2]) / len(recent_requests), 2) if recent_requests else 0
    error_count = len([code for code in ip_status_log[ip] if code >= 400])
    total_count = len(ip_status_log[ip])
    error_rate = round(error_count / total_count, 2) if total_count > 0 else 0
    is_bot_ua = 1 if any(x in user_agent.lower() for x in ["curl", "bot", "scanner", "sqlmap"]) else 0
    unique_urls = len(ip_url_log[ip])

    features = [[
        len(recent_requests),
        status_code,
        unique_urls,
        error_rate,
        burst_ratio,
        is_bot_ua
    ]]

    try:
        prediction = int(model.predict(features)[0])
        label_text = LABEL_MAP.get(prediction, "❓ Unknown")
    except Exception as e:
        print(f"❌ [track()] prediction hatası: {e}")
        prediction = 5  # fallback → "Other"
        label_text = LABEL_MAP.get(prediction, "❓ Unknown")

    # ✅ CSV'ye yazımı her durumda yap
    log_entry = pd.DataFrame([{
        "timestamp": timestamp,
        "source_ip": ip,
        "url": url,
        "user_agent": user_agent,
        "status_code": status_code,
        "label": prediction
    }])
    write_header = not os.path.exists(LOG_FILE)
    log_entry.to_csv(LOG_FILE, mode='a', header=write_header, index=False)

    # Dashboard'a gönder
    socketio.emit("new_request", {
        "ip": ip,
        "url": url,
        "timestamp": timestamp.strftime("%H:%M:%S"),
        "is_attack": int(prediction != 0),
        "label": label_text
    })

    if prediction != 0:
        register_attack()

        coords = get_coordinates(ip)
        country = resolve_country(ip)

        if coords:
            socketio.emit("new_attack", {
                "ip": ip,
                "country": country,
                "coords": coords
            })
        else:
            print(f"❌ Koordinat bulunamadı: {ip}")

        if check_alarm() and should_send_email():
            recent_ips = [ip for ip in ip_request_log if ip_status_log[ip][-1] >= 400 or "curl" in ''.join(ip_url_log[ip])]
            ip_counter = Counter(recent_ips)
            top_attackers = [ip for ip, _ in ip_counter.most_common(3)]
            send_alert_email(attack_count=len(recent_ips), top_ips=top_attackers)

            try:
                yag = yagmail.SMTP(config_email.EMAIL_ADDRESS, config_email.EMAIL_PASSWORD)
                yag.send(
                    to=config_email.TO_ADDRESS,
                    subject="🚨 Rex Alert: High Attack Rate Detected",
                    contents="More than 15 attacks were detected within 30 seconds.\n\nCheck the dashboard for more details."
                )
                print("📧 Alarm maili gönderildi!")
            except Exception as e:
                print(f"❌ Mail gönderilemedi: {e}")

        attack_data = pd.DataFrame([{
            "Time": timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "IP Address": ip,
            "Country": resolve_country(ip),
            "User Agent": user_agent,
            "URL": url,
            "HTTP Status": status_code,
            "Requests in Last 10s": len(recent_requests),
            "Unique URLs": unique_urls,
            "Error Rate": error_rate,
            "Burst Ratio": burst_ratio,
            "Bot-Like Agent": "Yes" if is_bot_ua else "No",
            "Label": label_text
        }])

        write_attack_header = not os.path.exists(ATTACK_LOG_FILE)
        attack_data.to_csv(ATTACK_LOG_FILE, mode='a', header=write_attack_header, index=False)

    print(f"[DEBUG] features: {features} → Prediction: {prediction}")
    return "OK"


@app.route("/api/normal-requests")
def api_normal_requests():
    if not os.path.exists(LOG_FILE):
        return {"labels": [], "counts": []}

    df = pd.read_csv(LOG_FILE)
    if "label" not in df.columns or "source_ip" not in df.columns:
        return {"labels": [], "counts": []}

    # Sadece label=0 olanlar (NORMAL)
    normal_df = df[df["label"] == 0]
    ip_counts = normal_df["source_ip"].value_counts().head(10)

    return {
        "labels": ip_counts.index.tolist(),
        "counts": ip_counts.values.tolist()
    }


@app.route("/label")
def label_data():
    if not os.path.exists(LOG_FILE):
        return "<h3>No data found.</h3>"

    df = pd.read_csv(LOG_FILE)

    if "label" not in df.columns:
        df["label"] = -1  # Henüz etiketlenmemiş

    df = df.tail(20)[::-1]

    rows = ""
    for idx, row in df.iterrows():
        rows += f"""
        <tr>
            <td>{row['timestamp']}</td>
            <td>{row['source_ip']}</td>
            <td>{row['url']}</td>
            <td>{row['user_agent']}</td>
            <td>{row['status_code']}</td>
            <td>
                <form method="POST" action="/submit-label" style="display:flex; gap:5px;">
                    <input type="hidden" name="idx" value="{idx}">
                    <select name="label">
                        <option value="0" {'selected' if row['label']==0 else ''}>✅ Normal</option>
                        <option value="1" {'selected' if row['label']==1 else ''}>🚨 DDoS</option>
                        <option value="2" {'selected' if row['label']==2 else ''}>🔓 Brute-force</option>
                        <option value="3" {'selected' if row['label']==3 else ''}>🕵️ Port Scan</option>
                        <option value="4" {'selected' if row['label']==4 else ''}>🧬 SQLi</option>
                        <option value="5" {'selected' if row['label']==5 else ''}>❓ Other</option>
                    </select>
                    <button type="submit">Kaydet</button>
                </form>
            </td>
        </tr>
        """

    return f"""
    <html>
    <head>
        <title>Rex – Veri Etiketleme</title>
        <style>
            body {{ font-family: Arial; background: #121212; color: #eee; padding: 30px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th, td {{ border: 1px solid #333; padding: 10px; text-align: center; }}
            select, button {{ padding: 5px; }}
        </style>
    </head>
    <body>
        <h2>🧪 Veri Etiketleme Paneli</h2>
        <table>
            <tr>
                <th>Zaman</th>
                <th>IP</th>
                <th>URL</th>
                <th>User Agent</th>
                <th>Status</th>
                <th>Etiket</th>
            </tr>
            {rows}
        </table>
    </body>
    </html>
    """

@app.route("/submit-label", methods=["POST"])
def submit_label():
    idx = int(request.form["idx"])
    label = int(request.form["label"])

    df = pd.read_csv(LOG_FILE)
    if "label" not in df.columns:
        df["label"] = -1  # default: unlabeled

    df.loc[idx, "label"] = label
    df.to_csv(LOG_FILE, index=False)

    return "<script>window.location.href='/label';</script>"


def get_coordinates(ip):
    try:
        response = geoip_reader.city(ip)
        return (response.location.latitude, response.location.longitude)
    except:
        return None


def send_alert_email(attack_count, top_ips):
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = f"""
    <h2 style='color: crimson;'>🚨 Rex Alert: High Attack Volume</h2>
    <p><b>Time:</b> {now_str}</p>
    <p><b>Attacks in last 30s:</b> {attack_count}</p>
    <p><b>Top Offenders:</b></p>
    <ul>
        {''.join(f'<li>{ip}</li>' for ip in top_ips)}
    </ul>
    <p><a href='http://127.0.0.1:5000' style='padding: 10px 15px; background: crimson; color: white; text-decoration: none; border-radius: 5px;'>View Dashboard</a></p>
    """

    try:
        yag = yagmail.SMTP(config_email.EMAIL_ADDRESS, config_email.EMAIL_PASSWORD)
        yag.send(
            to=config_email.TO_ADDRESS,
            subject="🚨 Rex Alert: High Attack Rate Detected",
            contents=[html]
        )
        print("📧 Havalı alarm maili gönderildi!")
    except Exception as e:
        print(f"❌ Mail gönderilemedi: {e}")

@app.route("/attack-log")
def attack_log():
    if not os.path.exists(ATTACK_LOG_FILE):
        return "<h3>No attack data yet.</h3>"

    df = pd.read_csv(ATTACK_LOG_FILE)
    df = df.tail(50)[::-1]

    html = df.to_html(
        index=False,
        classes="attack-table",
        border=0,
        justify="center"
    )

    return f"""
    <html>
    <head>
        <title>Rex - Attack Log</title>
        <meta http-equiv="refresh" content="10"> <!-- ✅ Otomatik yenileme -->
        <style>
            body {{
                font-family: Arial, sans-serif;
                padding: 30px;
                background-color: #121212;
                color: #eee;
            }}
            h2 {{
                color: crimson;
            }}
            .attack-table {{
                border-collapse: collapse;
                width: 100%;
                background-color: #1e1e1e;
                color: #fff;
            }}
            .attack-table th, .attack-table td {{
                border: 1px solid #333;
                padding: 8px 12px;
                text-align: center;
            }}
            .attack-table th {{
                background-color: #292929;
            }}
            .attack-table tr:nth-child(even) {{
                background-color: #2c2c2c;
            }}
        </style>
    </head>
    <body>
        <h2>🚨 Attack Log (Last 50 Entries)</h2>
        <p style="font-size:14px; color: gray;">Auto-refresh every 10 seconds</p>
        {html}
    </body>
    </html>
    """

GEOIP_DB_PATH = "geoip/GeoLite2-City.mmdb"
geoip_reader = geoip2.database.Reader(GEOIP_DB_PATH)


def resolve_country(ip):
    try:
        response = geoip_reader.country(ip)
        return response.country.name
    except:
        return "Unknown"
    


@app.route("/api/hourly-attack-data")
def api_hourly_attack_data():
    if not os.path.exists(ATTACK_LOG_FILE):
        return {"labels": [], "counts": []}

    df = pd.read_csv(ATTACK_LOG_FILE)
    if "Time" not in df.columns:
        return {"labels": [], "counts": []}

    df["Time"] = pd.to_datetime(df["Time"])
    df["Hour"] = df["Time"].dt.strftime("%H:00")

    grouped = df.groupby("Hour").size().sort_index()
    labels = grouped.index.tolist()
    counts = grouped.values.tolist()

    return {"labels": labels, "counts": counts}

@app.route("/api/label-distribution")
def api_label_distribution():
    if not os.path.exists(LOG_FILE):
        return {"labels": [], "counts": []}

    df = pd.read_csv(LOG_FILE)
    if "label" not in df.columns:
        return {"labels": [], "counts": []}

    counts = df["label"].value_counts().sort_index()
    
    labels = []
    values = []
    for label_id, count in counts.items():
        label_text = LABEL_MAP.get(label_id, f"Unknown {label_id}")
        labels.append(label_text)
        values.append(count)

    return {"labels": labels, "counts": values}

@app.route("/api/hourly-stacked-data")
def api_hourly_stacked_data():
    if not os.path.exists(LOG_FILE):
        return {"labels": [], "datasets": []}

    df = pd.read_csv(LOG_FILE)
    if "label" not in df.columns or "timestamp" not in df.columns:
        return {"labels": [], "datasets": []}

    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df["hour"] = df["timestamp"].dt.strftime("%H:00")

    grouped = df.groupby(["hour", "label"]).size().unstack(fill_value=0).sort_index()

    response = {
        "labels": grouped.index.tolist(),
        "datasets": []
    }

    for label_id in grouped.columns:
        response["datasets"].append({
            "label": LABEL_MAP.get(label_id, f"Label {label_id}"),
            "data": grouped[label_id].tolist()
        })

    return response


# 🧠 Rex'i çalıştır
if __name__ == "__main__":
    print("🧠 Rex is live at http://127.0.0.1:5000")
    socketio.run(app)
