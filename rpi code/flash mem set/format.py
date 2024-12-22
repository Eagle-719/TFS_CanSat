import machine
import os
import winbond
flash = winbond.W25QFlash(spi = SPI(0, baudrate=80_000_000,
                                     sck=Pin(6), mosi=Pin(7), miso=Pin(4)),
                          cs=machine.Pin(5),
                          baud=2000000,
                          software_reset=True)

print('formatting')
flash.format()

print('flashing')
os.VfsFat.mkfs(flash)

os.umount('/external')

print('mounting to external')
os.mount(flash, '/external')