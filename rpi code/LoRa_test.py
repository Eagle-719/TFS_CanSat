from machine import Pin,UART

uart = UART(1, baudrate=115200, tx=Pin(8), rx=Pin(9))

uart.init(bits=8, parity=None, stop=1, flow=0)

uart.write(b'radio tx 48656c6c6f20576f726c6421 1\r\n')

while True:
    if uart.any():
        print(uart.read())

