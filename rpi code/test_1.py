from machine import Pin, SPI

# Initialize SPI
spi = SPI(0, baudrate=80_000_000, polarity=0, phase=0,
          sck=Pin(6), mosi=Pin(7), miso=Pin(4))
cs = Pin(5, Pin.OUT)  # Chip Select Pin

def read_jedec_id():
    cs.value(0)  # Select the chip
    spi.write(b'\x9F')  # Send JEDEC ID command
    jedec_id = spi.read(3)  # Read 3 bytes of the JEDEC ID
    cs.value(1)  # Deselect the chip
    return jedec_id

print("JEDEC ID:", read_jedec_id())