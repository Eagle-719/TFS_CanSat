from machine import Pin, I2C, RTC
from utime import sleep
import utime
import math

from bmp280 import BMP280I2C

i2c0_sda = Pin(0)
i2c0_scl = Pin(1)
i2c0 = I2C(0, sda=i2c0_sda, scl=i2c0_scl, freq=400000)
bmp280_i2c = BMP280I2C(0x76, i2c0)

while True:
    t = utime.ticks_ms()
    readout = bmp280_i2c.measurements
    temp = math.floor(readout['t']*10)/10
    pres = readout['p']
    
    alt = (math.log(pres/1011)*8.3144598*301)/(9.81)
    alt = math.floor(alt*10)/10
    pres = math.floor(pres*10)/10
    print(f"Temperature : {temp} °C, pressure: {pres} hPa, altitude: {alt}")
    print(utime.ticks_ms() - t)