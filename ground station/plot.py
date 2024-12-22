import serial
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

temperature = []
pressure = []
humidity = []
timecode = []

fig, ax = plt.subplots(3, 1)
graph_t = ax[0].plot([], [], color = 'r')[0]
graph_p = ax[1].plot([], [], color = 'g')[0]
graph_h = ax[2].plot([], [], color = 'b')[0]
ser = serial.Serial('COM3', 115200, timeout=1)

def update(frame):
    line = ser.readline().decode('utf-8').strip()
    if line:
        l = line.split(" ")
        if len(l) != 4:
            return
        temperature.append(int(l[0]) / 100)
        pressure.append(int(l[1]) / 25600)
        humidity.append(int(l[2]) / 1024)
        timecode.append(int(l[3]) / 1000)

    graph_t.set_data(timecode, temperature)
    if len(timecode) > 0:
        ax[0].set_xlim(timecode[0], timecode[len(timecode) - 1])
        ax[0].set_ylim(min(temperature), max(temperature))

    graph_p.set_data(timecode, pressure)
    if len(timecode) > 0:
        ax[1].set_xlim(timecode[0], timecode[len(timecode) - 1])
        ax[1].set_ylim(min(pressure), max(pressure))

    graph_h.set_data(timecode, humidity)
    if len(timecode) > 0:
        ax[2].set_xlim(timecode[0], timecode[len(timecode) - 1])
        ax[2].set_ylim(min(humidity), max(humidity))

anim = FuncAnimation(fig, update, frames = None)
plt.show()

ser.close()