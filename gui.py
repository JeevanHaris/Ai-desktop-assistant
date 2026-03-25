import tkinter as tk
from tkinter import messagebox
from simulator import generate_sensor_data, detect_crash
from data import log_data
from datetime import datetime
import os

def generate_report(sensor):
    os.makedirs("reports", exist_ok=True)
    filename = f"reports/report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(filename, 'w') as f:
        f.write("✈️ Aircraft Crash Report\n")
        f.write(f"Time: {datetime.now()}\n")
        for k, v in sensor.items():
            f.write(f"{k.title()}: {v}\n")
    return filename

def run_simulation(label, status_label):
    sensor = generate_sensor_data()
    log_data(sensor)
    
    display_text = "\n".join([f"{k.title()}: {v}" for k, v in sensor.items()])
    label.config(text=display_text)

    if detect_crash(sensor):
        label.config(fg="red")
        status_label.config(text="⚠️ CRASH DETECTED!", bg="red", fg="white")
        report = generate_report(sensor)
        messagebox.showerror("⚠️ CRASH ALERT", f"Crash report saved:\n{report}")
    else:
        label.config(fg="lightgreen")
        status_label.config(text="✅ All Systems Normal", bg="green", fg="white")

def launch_gui():
    from data import init_csv
    init_csv()

    window = tk.Tk()
    window.title("Aircraft Crash Monitoring System")
    window.geometry("500x400")
    window.configure(bg='#1e1e2f')

    title = tk.Label(window, text="Aircraft Monitoring Dashboard", font=("Helvetica", 18, "bold"), bg='#1e1e2f', fg="skyblue")
    title.pack(pady=15)

    sensor_display = tk.Label(window, text="Sensor Data will appear here", font=("Consolas", 12), bg='#1e1e2f', fg="white", justify="left")
    sensor_display.pack(pady=20)

    status_display = tk.Label(window, text="System Status", font=("Helvetica", 14), bg="gray", fg="white", width=25)
    status_display.pack(pady=10)

    simulate_btn = tk.Button(window, text="Simulate Sensor Data", font=("Helvetica", 12, "bold"), bg="orange", fg="white", width=25,
                              command=lambda: run_simulation(sensor_display, status_display))
    simulate_btn.pack(pady=20)

    quit_btn = tk.Button(window, text="Exit", font=("Helvetica", 10), bg="red", fg="white", command=window.destroy)
    quit_btn.pack(pady=10)

    window.mainloop()

if __name__ == "__main__":
    launch_gui()
