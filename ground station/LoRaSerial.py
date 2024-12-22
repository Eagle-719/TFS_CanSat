import serial

with serial.Serial('COM4', 115200, timeout=1) as ser:
    ser.write(b"radio rxstop\r\n")
    a = 0
    while True:
        if a%3 == 0:
            ser.write(b"\r\n")
        line = ser.readline().decode().strip()
        if len(line) > 0:
            print(line)
        a+=1