from network import LoRa
import socket
import machine
from machine import I2C, RTC, UART, Timer
import struct
import ubinascii
import time

import lc709203f
import ds3231
import si7021
import si1145
import pms5003


I2C_SDA = 'P22'
I2C_SCL = 'P23'
UART_TXD = 'P14'
UART_RXD = 'P15'
PMS_RESET = 'P20'
PMS_EN = 'P21'


def send_lora_msg(pms_data):
    # Initialise LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    # create an OTAA authentication parameters
    app_eui = ubinascii.unhexlify('ADA4DAE3AC34676B')
    app_key = ubinascii.unhexlify('C230A4272B0C4A61916EF5D9C3F70694')
    dev_eui = lora.mac()
    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # set the LoRaWAN pms_data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    # make the socket blocking
    # (waits for the pms_data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)
    # send pms_data
    s.send(pms_data)
    # make the socket non-blocking
    # (because if there's no pms_data received it will block forever...)
    s.setblocking(False)
    # get any pms_data received (if any...)
    pms_data = s.recv(64)


i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=(I2C_SDA, I2C_SCL))
uart = UART(1, 9600, parity=None, stop=1, pins=(UART_TXD, UART_RXD))

si7021 = si7021.Si7021(i2c)
si1145 = si1145.Si1145(i2c)
pms5003 = pms5003.PMS5003(uart= uart, pin_enable=PMS_EN, pin_reset=PMS_RESET)
ds3231 = ds3231.DS3231(i2c)
try:
    lc709203f = lc709203f.BatteryMonitor(bus=i2c, battery_profile=0x0001, capacity=0x0036)
except:
    pass

chrono = Timer.Chrono()
chrono.start()

try:
    lc709203f.wakeup()
    volt = lc709203f.getBatteryVoltage()
    volt = int(round(volt, 3)*1000)
    lc709203f.sleep()
except:
    volt = 0
    pass

temp = si7021.temperature
rel_hum = si7021.relative_humidity
temp = int(round(temp, 2)*100)
rel_hum = int(round(rel_hum))

uv = si1145.read_uv
ir = si1145.read_ir
view = si1145.read_visible
uv = int(round(uv, 2)*100)

while (chrono.read() < 30): # Waiting for pms5003
    time.sleep(1)
chrono.stop()

try:
    pms_data = pms5003.read()
    pm25_standard = pms_data.pm_ug_per_m3(2.5)
    pm100_standard = pms_data.pm_ug_per_m3(10)
except:
    pm25_standard = 0
    pm100_standard = 0
    pass

pms5003.sleep()

# take timestamp from LoPy RTC because ds3231 doesn't give it
rtc = RTC()
rtc.init(tuple(ds3231.DateTime()+[0, 0])) # datetime + [microseconds, tzinfo (ignored in microPython)]
timestamp = time.time()

msg_out = struct.pack('>8HL', temp, rel_hum, pm25_standard, pm100_standard,
                    uv, ir, view, volt, timestamp) # 20 bytes

send_lora_msg(msg_out)

minute, second = ds3231.DateTime()[4:6]
sleep_time = ((59-minute)*60)+(60-second) # seconds to next hour o'clock
machine.deepsleep(sleep_time*1000) 
