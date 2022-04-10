# This is your main script.
from machine import I2C
from LC709203F import BatteryMonitor
from time import sleep

i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))
FuelGauge = BatteryMonitor(bus=i2c, battery_profile=0x0001, capacity=0x0036)
print("FuelGauge is Ready")
while True:
    battMon = FuelGauge.selfTest()
    sleep(20)
