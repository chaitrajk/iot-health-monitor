import os
import zipfile

# --- Project structure and files ---
project_name = "SmartHealthMonitoring"
folders = {
    f"{project_name}/backend/templates": {},
    f"{project_name}/backend/static/css": {},
    f"{project_name}/backend/static/js": {},
    f"{project_name}/sensors": {}
}

files = {
    f"{project_name}/backend/app.py": """from flask import Flask, render_template, jsonify, request
from utils import check_alerts

app = Flask(__name__)

sensor_data = {"heart_rate": 0, "temperature": 0, "spo2": 0}

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/update', methods=['POST'])
def update_data():
    data = request.get_json()
    sensor_data.update(data)
    alert_message = check_alerts(sensor_data)
    return jsonify({"status": "success", "alert": alert_message})

@app.route('/data')
def get_data():
    return jsonify(sensor_data)

if __name__ == '__main__':
    app.run(debug=True)
""",
    f"{project_name}/backend/utils.py": """from twilio.rest import Client

TWILIO_SID = 'YOUR_TWILIO_SID'
TWILIO_AUTH = 'YOUR_TWILIO_AUTH_TOKEN'
TWILIO_PHONE = '+1234567890'
ALERT_PHONE = '+0987654321'

def send_sms(message):
    client = Client(TWILIO_SID, TWILIO_AUTH)
    client.messages.create(body=message, from_=TWILIO_PHONE, to=ALERT_PHONE)

THRESHOLDS = {"heart_rate": (60,100), "temperature": (36.1,37.5), "spo2": (95,100)}

def check_alerts(data):
    alerts = []
    for key, (low, high) in THRESHOLDS.items():
        if data[key] < low or data[key] > high:
            alerts.append(f"{key} out of safe range: {data[key]}")
    if alerts:
        message = "ALERT! " + ", ".join(alerts)
        send_sms(message)
        return message
    return None
""",
    f"{project_name}/backend/requirements.txt": "Flask\ntwilio\n",
    f"{project_name}/backend/templates/dashboard.html": """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Smart Health Dashboard</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
<h1>Real-Time Health Monitoring</h1>
<div>
    <p>Heart Rate: <span id="heart_rate">0</span> bpm</p>
    <p>Temperature: <span id="temperature">0</span> °C</p>
    <p>SpO2: <span id="spo2">0</span> %</p>
</div>

<script>
async function fetchData(){
    const res = await fetch('/data');
    const data = await res.json();
    document.getElementById('heart_rate').innerText = data.heart_rate;
    document.getElementById('temperature').innerText = data.temperature;
    document.getElementById('spo2').innerText = data.spo2;
}
setInterval(fetchData, 2000);
</script>
</body>
</html>
""",
    f"{project_name}/sensors/health_sensor.ino": """#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <ArduinoJson.h>

const char* ssid = "YOUR_WIFI";
const char* password = "YOUR_PASSWORD";
const char* serverUrl = "http://YOUR_PC_IP:5000/update";

void setup() {
  Serial.begin(115200);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) { delay(500); Serial.print("."); }
  Serial.println("Connected to WiFi");
}

void loop() {
  float heartRate = random(60, 110);
  float temperature = random(361, 380)/10.0;
  float spo2 = random(90, 100);

  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "application/json");
    String payload = "{\\"heart_rate\\":" + String(heartRate) + ",\\"temperature\\":" + String(temperature) + ",\\"spo2\\":" + String(spo2) + "}";
    int code = http.POST(payload);
    if(code>0) Serial.println(http.getString());
    http.end();
  }
  delay(5000);
}
""",
    f"{project_name}/README.md": """# Smart Health Monitoring System

**Stack:** Flask, NodeMCU (ESP8266), IoT Dashboard, Twilio API

## Features
- Real-time vitals tracking (Heart Rate, Temperature, SpO2)
- IoT Dashboard for live monitoring
- Alert SMS via Twilio if vitals go beyond safe limits

## Setup
1. Clone the repo
2. Install backend dependencies:

