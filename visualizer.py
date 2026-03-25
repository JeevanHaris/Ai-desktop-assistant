import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from simulator import generate_sensor_data
from data import log_data

times, altitudes, g_forces = [], [], []

def live_plot():
    fig, ax = plt.subplots()
    ax.set_title("Live Aircraft Sensor Data")
    ax.set_xlabel("Time (s)")
    altitude_line, = ax.plot([], [], label="Altitude (ft)")
    gforce_line, = ax.plot([], [], label="G-Force", color="r")
    ax.legend()

    def update(frame):
        sensor = generate_sensor_data()
        log_data(sensor)
        times.append(frame)
        altitudes.append(sensor['altitude'])
        g_forces.append(sensor['g_force'])

        altitude_line.set_data(times, altitudes)
        gforce_line.set_data(times, g_forces)
        ax.relim()
        ax.autoscale_view()
        return altitude_line, gforce_line

    ani = FuncAnimation(fig, update, interval=1000)
    plt.show()
