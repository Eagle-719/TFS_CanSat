from machine import Pin, PWM
import time
import math
import utime

# Choose a PWM pin (e.g., GPIO 16)
pwm_pin = PWM(Pin(16))

# Set PWM frequency (e.g., 1 kHz)
pwm_pin.freq(10000)

# Function to set output voltage
def set_voltage(pwm, voltage):
    if 0 <= voltage <= 3.3:
        duty_cycle = int((voltage / 3.3) * 65535)  # Convert to 16-bit duty cycle
        pwm.duty_u16(duty_cycle)
    else:
        print("Voltage out of range (0-3.3V)")

while True:
    set_voltage(pwm_pin, 1 + (math.sin(utime.ticks_ms()/1000) + 1)/2)