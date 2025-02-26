from machine import UART, Pin, I2C
import uasyncio as asyncio
import time
import struct
import bme280
import math

uart_lora = UART(1, baudrate=115200, tx=Pin(4), rx=Pin(5))
uart_gps = UART(0, baudrate=38400, tx=Pin(16), rx=Pin(17))
i2c_bme = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000)
i2c_hw290 = I2C(1,sda=Pin(10), scl=Pin(11), freq=400000)
bme = bme280.BME280(i2c=i2c_bme)
gyro_rot = [0, 0, 0]
gps = [0, 0, 0]
data_lock = _thread.allocate_lock()
ahrs = MahonyAHRS(sample_period=0.001, kp=0.5, ki=0.1)

def send_command(uart, command):
    uart.write(command + '\r\n')
    time.sleep(0.05)
    response = uart.read()
    if response:
        return response.decode('utf-8').strip()
    return ''

def radio_rx():
    response = send_command(uart_lora, "radio rx 0")
    if "ok" in response.lower():
        return 0
    else:
        return response.lower()

def radio_tx(data, count):
    command = f"radio tx {data} {count}"
    response = send_command(uart_lora, command)
    if "ok" in response.lower():
        return 0
    else:
        return response.lower()

def convert_to_decimal(coord, direction):
    if not coord or not direction:
        return "NA"
    try:
        degrees = int(coord[:2]) if direction in ['N', 'S'] else int(coord[:3])
        minutes = float(coord[2:])
        decimal = degrees + (minutes / 60)
        if direction in ['S', 'W']:
            decimal = -decimal
        return decimal
    except ValueError:
        return None

def read_gps_data():
    while not uart_gps.any():
        time.sleep(0)
    if uart_gps.any():
        nmea_sentence = uart_gps.readline().decode('utf-8').strip()
        sentences = nmea_sentence.split("$")
        for sentence in sentences:
            if sentence == "":
                continue
            #print(sentence)
            if sentence.startswith("GNGGA"):
                fields = sentence.split(",")
                r = []
                if len(fields) > 9:
                    r.append(convert_to_decimal(fields[2], fields[3]))
                    r.append(convert_to_decimal(fields[4], fields[5]))
                    r.append(fields[9])
                    r.append(fields[6])
                    r.append(int(fields[7]))
                    return r
    return []

def set_gga_rate(measRate):
    navRate = 1  # Navigation rate (number of measurement cycles per navigation solution)
    timeRef = 0  # Time reference (0 for UTC, 1 for GPS)

    # Construct the payload
    payload = struct.pack('<HHH', measRate, navRate, timeRef)

    # Calculate the length of the payload
    length = len(payload)

    # Calculate the checksum
    ck_a = 0
    ck_b = 0
    for byte in [0x06, 0x08, length & 0xFF, (length >> 8) & 0xFF] + list(payload):
        ck_a = (ck_a + byte) & 0xFF
        ck_b = (ck_b + ck_a) & 0xFF

    # Construct the full message
    ubx_msg = struct.pack('<BBBBBB', 0xB5, 0x62, 0x06, 0x08, length & 0xFF, (length >> 8) & 0xFF) + payload + struct.pack('<BB', ck_a, ck_b)

    uart_gps.write(ubx_msg)

def calculate_altitude(pressure):
    return 0
    #return 44330 * (1 - (int(pressure) / 101325) ** 0.1903)

async def gyro(i2c):
    while True:
        gx, gy, gz, ax, ay, az, mx, my, mz = read_sensors()
        ahrs.update(gx, gy, gz, ax, ay, az, mx, my, mz)
        roll, pitch, yaw = ahrs.get_euler()
        
        data_lock.acquire()
        gyro_rot = [roll, pitch, yaw]
        data_lock.release()
        
        await asyncio.sleep(0)

async def navigation():
    while True:
        data_lock.acquire()
        x, y, z = gps
        yaw = gyro_rot[2]
        data_lock.release()
        
        """
        TODO: Navigation code
        """
        
        await asyncio.sleep(0)

def main_cycle(bme):
    set_gga_rate(1000)
    N = 1
    while True:
        if len(r) > 4:
            t, p, h = bme.read_compensated_data()
            
            r = await read_gps_data()
            
            data_lock.acquire()
            gps = [r[0], r[1], r[2]]
            data_lock.release()
            
            response = radio_tx(f"TFS{N},{t/100},{p/25600},{calculate_altitude(p/256)},{r[0]},{r[1]},{r[2]}".encode().hex(), 3)
            #print(f"Radio: {response} Sat: {r[4]}  Fix: {r[3]}")

            N += 1
        time.sleep(0.01)
        
async def main():
    asyncio.create_task(gyro(i2c_hw290))
    asyncio.create_task(task2())
    await asyncio.Event().wait()
        

_thread.start_new_thread(main_cycle(bme), ())
asyncio.run(main())



