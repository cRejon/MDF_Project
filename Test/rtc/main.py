import time
from machine import I2C
import ds3231
from machine import RTC
from network import WLAN
import machine

wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid='vodafone0548', auth=(WLAN.WPA2, 'MMKJYXJM4UZM2E'))
while not wlan.isconnected():
    machine.idle()
print("WiFi connected succesfully")
print(wlan.ifconfig())


i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000)

ds = ds3231.DS3231(i2c)

rtc = RTC()
rtc.ntp_sync("pool.ntp.org")
while not rtc.synced():
    #pass
    machine.idle()
print("RTC syncronized")
print(rtc.now())

now = rtc.now()


ds.Date([now[0],now[1],now[2]])
ds.Time([now[3],now[4],now[5]])

print(ds.DateTime())
