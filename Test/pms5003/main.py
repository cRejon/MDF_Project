import machine
from pms5003 import PMS5003
import time

uart = machine.UART(1, 9600, parity=None, stop=1, pins=('P14','P15'))

# Configure the PMS5003
pms5003 = PMS5003(uart= uart, pin_enable='P21', pin_reset='P20')
print("Warming up the sensor")
time.sleep(30)

data = pms5003.read()
print(data)
print(data.pm_ug_per_m3(2.5))
print(data.pm_ug_per_m3(10))

print("Turning off the sensor")
pms5003.sleep()
time.sleep(1)

print("Entering in deep sleep")
machine.deepsleep((60*1000))
