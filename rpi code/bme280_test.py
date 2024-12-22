from machine import Pin, I2C      #importing relevant modules & classes
from time import sleep
import utime
import bme280       #importing BME280 library

i2c=I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)    #initializing the I2C method 

print('Entered bme280_test.py')

flash_mount_point = '/external'     # use same as in boot.py
external_bme280_test_file_name = 'dat_bme280_test.txt'
external_test_file_path = flash_mount_point + '/' + external_bme280_test_file_name


with open(external_test_file_path, 'w') as file:
    file.close()


bme = bme280.BME280(i2c=i2c)   #BME280 object created
start = utime.ticks_ms()
while True:
  
    t,p,h = bme.read_compensated_data()
  
    print(str(t) + " " + str(p) + " " + str(h) + " " + str(utime.ticks_ms() - start))
  
  
  
    with open(external_test_file_path, 'a') as file:
        file.write(str(t) + " ") #temp
        file.write(str(p) + " ") #pressure
        file.write(str(h) + " ") #humidity
        file.write(str(utime.ticks_ms() - start)) #relative timecode
        file.write('\n')
        file.close()
    
    #sleep(0.01)           #delay of 0.1m