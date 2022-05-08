import time
from machine import I2C
import ds3231

i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))

ds = ds3231.DS3231(i2c)

while True:
    print(ds.DateTime())
    time.sleep(5)