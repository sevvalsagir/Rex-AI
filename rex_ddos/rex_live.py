from flask import Flask, request
from datetime import datetime
import pandas as pd
from collections import defaultdict
import os

app = Flask(__name__)

# File where requests will be logged
LOG_FILE = "live_log.csv"

# Dictionary to track requests per IP address
ip_request_log = defaultdict(list)

# Detection threshold: More than 5 requests in 10 seconds = suspicious
THRESHOLD = 5
TIME_WINDOW = 10  # seconds

@app.route("/", methods=["GET"])
def track_request():
    ip = request.remote_addr
    url = request.path
    timestamp = datetime.now()

    # 1. Log the request to CSV file
    log_entry = pd.DataFrame([{
        "timestamp": timestamp,
        "source_ip": ip,
        "url": url
    }])
    
    write_header = not os.path.exists(LOG_FILE)
    log_entry.to_csv(LOG_FILE, mode="a", header=write_header, index=False)

    # 2. Analyze request frequency per IP
    ip_request_log[ip].append(timestamp)

    # Filter only recent requests within TIME_WINDOW
    recent_requests = [t for t in ip_request_log[ip] if (timestamp - t).seconds < TIME_WINDOW]
    ip_request_log[ip] = recent_requests  # Clean old entries

    if len(recent_requests) > THRESHOLD:
        return (
            f"🚨 Suspicious traffic detected!\n"
            f"IP: {ip}\n"
            f"Requests in last {TIME_WINDOW} seconds: {len(recent_requests)}\n", 
            429
        )

    return (
        f"✅ Request received\n"
        f"IP: {ip}\n"
        f"Time: {timestamp.strftime('%H:%M:%S')}\n"
    )

if __name__ == "__main__":
    print("🛡️ Rex is live and monitoring at http://127.0.0.1:5000")
    app.run(debug=True)
