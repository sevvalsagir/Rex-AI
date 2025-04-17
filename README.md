# Rex: Real-Time Web Attack Detection and Monitoring System

Rex is a real-time web traffic analysis and intrusion detection system designed to detect and classify malicious HTTP requests. It monitors inbound traffic, extracts behavioral features from request patterns, and uses a trained machine learning model to identify various types of web-based attacks such as DDoS, brute-force, port scanning, and SQL injection.

The system provides a real-time dashboard for visualization, alerting, and model retraining, making it suitable for research, simulations, and educational purposes.

## Features

- Real-time HTTP traffic analysis and classification
- Detection of multiple attack types (multi-class model)
- Behavioral feature extraction (burst rate, error rate, request frequency, etc.)
- Live request logging and attack reporting
- WebSocket-based live dashboard interface
- Interactive data labeling panel
- Model retraining functionality using labeled logs
- Dark/light mode dashboard UI
- GeoIP-based IP visualization
- Attack history and trend analysis with dynamic charts

## Technologies Used

- **Backend**: Python, Flask, Flask-SocketIO
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Frontend**: HTML5, CSS3, JavaScript (Chart.js, Leaflet.js)
- **Data Storage**: CSV-based logging (pandas)
- **Geolocation**: MaxMind GeoLite2 database
- **Email Alerts**: yagmail integration for threshold-based alerting

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/rex-dashboard.git
   cd rex-dashboard
