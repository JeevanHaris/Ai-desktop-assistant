import random

def generate_sensor_data():
    return {
        'altitude': round(random.uniform(100, 35000), 2),
        'speed': round(random.uniform(150, 850), 2),
        'temperature': round(random.uniform(-50, 50), 2),
        'g_force': round(random.uniform(0, 12), 2),
    }

def detect_crash(sensor):
    return sensor['altitude'] < 1000 and sensor['g_force'] > 6
