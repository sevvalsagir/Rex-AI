from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from datetime import datetime
import pandas as pd
import os
from joblib import load

app = Flask(__name__)
socketio = SocketIO(app)
LOG_FILE = "live_log.csv"

@app.route("/")
def dashboard():
    return render_template("dashboard.html")

@app.route("/track", methods=["GET"])
def track():
    model = load("model/rex_model.pkl")
    ip = request.remote_addr
    url = request.path
    timestamp = datetime.now()

    log_entry = pd.DataFrame([{
        "timestamp": timestamp,
        "source_ip": ip,
        "url": url
    }])

    write_header = not os.path.exists(LOG_FILE)
    log_entry.to_csv(LOG_FILE, mode="a", header=write_header, index=False)

    # Send data to frontend via socket
    socketio.emit("new_request", {
        "ip": ip,
        "url": url,
        "timestamp": timestamp.strftime("%H:%M:%S")
    })

        # Simulate features for the model
    requests_in_10s = ip_request_log[ip].count(lambda t: (timestamp - t).seconds < 10)
    status_code = 200  # For now, you can replace with real code if you parse one
    features = [[requests_in_10s, status_code]]

    prediction = model.predict(features)[0]

    # Send to dashboard
    socketio.emit("new_request", {
        "ip": ip,
        "url": url,
        "timestamp": timestamp.strftime("%H:%M:%S"),
        "is_attack": int(prediction)
    })

    return "OK"

if __name__ == "__main__":
    print("🖥️ Rex Dashboard running at http://127.0.0.1:5000")
    socketio.run(app)
