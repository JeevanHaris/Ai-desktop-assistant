import csv
import os
from datetime import datetime

CSV_FILE = "logs/sensor_log.csv"

def init_csv():
    os.makedirs("logs", exist_ok=True)
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Time', 'Altitude', 'Speed', 'Temperature', 'G-Force'])

def log_data(sensor):
    with open(CSV_FILE, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            sensor['altitude'],
            sensor['speed'],
            sensor['temperature'],
            sensor['g_force']
        ])
