from machine import UART
from pms5003 import PMS5003
import time

uart = UART(1, 9600, parity=None, stop=1, pins=('P14','P15'))

# Configure the PMS5003 
pms5003 = PMS5003(uart= uart, pin_enable='P17', pin_reset='P16')
time.sleep(30)
while True:
    data = pms5003.read()
    print(data)
    print(data.pm_ug_per_m3(2.5))
    print(data.pm_ug_per_m3(10))
    time.sleep(5)
