import serial

with serial.Serial('COM4', 115200, timeout=1) as ser:
    ser.write(b"radio rx 0\r\n")
    while True:
        line = ser.readline().decode().strip()
        if len(line) > 0:
            print(line)