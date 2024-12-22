import machine
import utime

led_pin= machine.Pin(25, machine.Pin.OUT)

while True:
    led_pin.value(1) #turn led on
    utime.sleep (1) #wait for 1 secs
    led_pin.value(0) #turn led off
    utime.sleep (1) #wait for 1 secs