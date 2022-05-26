import time
from machine import I2C, RTC
import ds3231

i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))

ds3231 = ds3231.DS3231(i2c)

# ds3231 doesn't give timestamp
rtc = RTC()
print(ds3231.DateTime())
rtc.init(tuple(ds3231.DateTime()+[0, 0])) # [microseconds, tzinfo (ignored in microPython)]

while True:
    now = rtc.now()
    print("Now: ", now)
    timestamp = time.time()
    print("Timestamp: ", timestamp)
    time.sleep(5)
