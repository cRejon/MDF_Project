from network import LoRa
import socket
from machine import I2C, RTC, UART, Timer
import struct
import ubinascii
import time

import lc709203f
import ds3231
import si7021
import si1145
import pms5003


i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))
uart = UART(1, 9600, parity=None, stop=1, pins=('P14','P15'))

si7021 = si7021.Si7021(i2c)
si1145 = si1145.Si1145(i2c)
pms5003 = pms5003.PMS5003(uart, set='P17', reset='P16')
ds3231 = ds3231.DS3231(i2c)
lc709203f = lc709203f.BatteryMonitor(bus=i2c, battery_profile=0x0001, capacity=0x0036)


def send_lora_msg(data):
    # Initialise LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    # create an OTAA authentication parameters
    app_eui = ubinascii.unhexlify('ADA4DAE3AC12676B')
    app_key = ubinascii.unhexlify('C230A4272B0D4A61916EF6D9C3F80694')
    #dev_eui = ('70B3D54991EA6F2E')
    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    # wait until the module has joined the network
    while not lora.has_joined():
        time.sleep(2.5)
        print('Not yet joined...')
    print('Joined')
    # create a LoRa socket
    s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)
    # set the LoRaWAN data rate
    s.setsockopt(socket.SOL_LORA, socket.SO_DR, 5)
    # make the socket blocking
    # (waits for the data to be sent and for the 2 receive windows to expire)
    s.setblocking(True)
    # send some data
    s.send(data)
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)
    # get any data received (if any...)
    data = s.recv(64)
    print(data)

while True:

    pms5003.set_pms()

    chrono = Timer.Chrono()
    chrono.start()

    lc709203f.wakeup()
    volt = lc709203f.getBatteryVoltage()
    print("Batt. Volt:         {}".format(volt))
    print("Batt. Residual Cap.:", lc709203f.getCapacity())
    print("Batt. Empty:", lc709203f.getEmpty())
    print("Direction: ", lc709203f.getCurrentDirection())
    lc709203f.sleep()

    temp = si7021.temperature
    rel_hum = si7021.relative_humidity
    print('Temperature:         {}'.format(temp))
    print('Relative Humidity:   {}'.format(rel_hum))

    uv = si1145.read_uv
    ir = si1145.read_ir
    view = si1145.read_visible
    print('UV:         {}'.format(uv))
    print('IR:   {}'.format(ir))
    print('Visible:   {}'.format(view))

    while (chrono.read() < 30):
        time.sleep(1)
    
    pm25_standard, pm100_standard  = pms5003.read_pms()[1:2]

    # ds3231 doesn't give timestamp
    rtc = RTC()
    rtc.init((ds3231.DateTime(), 0, 0)) # microseconds, tzinfo (ignored)
    time.timezone(3600)
    timestamp = time.time()
    print("Timestamp: ", timestamp)

    msg_out = struct.pack('>8HL', temp, rel_hum, pm25_standard, pm100_standard,
                        uv, ir, view, volt, timestamp)

    print(struct.calcsize('8HL'))

    #send_lora_msg(msg_out)

    chrono.stop()
    lapse = chrono.read()
    print("Lapse: ", lapse)

    #https://docs.pycom.io/datasheets/development/lopy/#deep-sleep
    #machine.deepsleep((3600*1000)-lapse, False)
    #machine.sleep((180*1000)-lapse)
