
from network import WLAN
import machine
from machine import I2C, RTC
import ds3231

i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))
ds3231 = ds3231.DS3231(i2c)

wlan = WLAN(mode=WLAN.STA)
wlan.connect(ssid='vodafone0548', auth=(WLAN.WPA2, 'MMKJYXJM4UZM2E'))
while not wlan.isconnected():
    machine.idle()
print("WiFi connected succesfully")
print(wlan.ifconfig())
rtc = RTC()
rtc.ntp_sync("pool.ntp.org")
while not rtc.synced():
    #pass
    machine.idle()
print("RTC syncronized")
now = rtc.now()
ds3231.Date([now[0],now[1],now[2]])
ds3231.Time([now[3],now[4],now[5]])
print(ds3231.DateTime())
wlan.disconnect()
wlan.deinit()

i2c.deinit()
