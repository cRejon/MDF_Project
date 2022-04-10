from network import LoRa
import socket
from machine import I2C, RTC, Pin, UART, Timer
import machine
import struct
import ubinascii
import time

import lc709203f
import ds3231
import si7021
import sgp30
import si1145
import pms5003


i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))
uart = UART(1, 9600, parity=None, stop=1, pins=('P15','P14'))

lc709203f = lc709203f.BatteryMonitor(bus=i2c, battery_profile=0x0001, capacity=0x0036)
ds3231 = ds3231.DS3231(i2c)
si7021 = si7021.Si7021(i2c)
#sgp30 = sgp30.Adafruit_SGP30(i2c)
si1145 = si1145.Si1145(i2c)
#pms5003 = pms5003.PMS5003(uart, set='P17', reset='P16')



def send_lora_msg(data):
    # Initialise LoRa in LORAWAN mode.
    lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)
    # create an OTAA authentication parameters
    app_eui = ubinascii.unhexlify('ADA4DAE3AC12676B')
    app_key = ubinascii.unhexlify('C230A4272B0D4A61916EF6D9C3F80694')
    #uncomment to use LoRaWAN application provided dev_eui
    #dev_eui = ('70B3D549938EA1EE')
    # join a network using OTAA (Over the Air Activation)
    lora.join(activation=LoRa.OTAA, auth=(app_eui, app_key), timeout=0)
    #lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)
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
    """
    # make the socket non-blocking
    # (because if there's no data received it will block forever...)
    s.setblocking(False)
    # get any data received (if any...)
    data = s.recv(64)
    print(data)
    """



def read_sgp30():
    # Initialize SGP-30 internal drift compensation algorithm.
    sgp30.iaq_init()
    # Wait 15 seconds for the SGP30 to properly initialize
    print("Waiting 15 seconds for SGP30 initialization.")
    time.sleep(15)
    # Retrieve previously stored baselines, if any (helps the compensation algorithm).
    has_baseline = False
    try:
        f_co2 = open('co2eq_baseline.txt', 'r')
        f_tvoc = open('tvoc_baseline.txt', 'r')

        co2_baseline = int(f_co2.read())
        tvoc_baseline = int(f_tvoc.read())
        #Use them to calibrate the sensor
        sgp30.set_iaq_baseline(co2_baseline, tvoc_baseline)

        f_co2.close()
        f_tvoc.close()

        has_baseline = True
    except:
        print('Impossible to read SGP30 baselines!')

    #Store the time at which last baseline has been saved
    baseline_time = time.time()

    co2_eq, tvoc = sgp30.iaq_measure()
    print('co2eq = ' + str(co2_eq) + ' ppm \t tvoc = ' + str(tvoc) + ' ppb')

    # Baselines should be saved after 12 hour the first timen then every hour,
    # according to the doc.
    if (has_baseline and (time.time() - baseline_time >= 3600)) \
            or ((not has_baseline) and (time.time() - baseline_time >= 43200)):

        print('Saving baseline!')
        baseline_time = time.time()

        try:
            f_co2 = open('co2eq_baseline.txt', 'w')
            f_tvoc = open('tvoc_baseline.txt', 'w')

            bl_co2, bl_tvoc = sgp30.get_iaq_baseline()
            f_co2.write(str(bl_co2))
            f_tvoc.write(str(bl_tvoc))

            f_co2.close()
            f_tvoc.close()

            has_baseline = True
        except:
            print('Impossible to write SGP30 baselines!')

    return co2_eq

while True:
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

    """
    co2_eq.set_iaq_rel_humidity(rel_hum, temp)
    co2_eq = read_sgp30()
    print('Equivalent C02:      {}'.format(co2_eq))


    pms5003.set_pms()
    pm10_standard, pm25_standard, pm100_standard, pm10_env, \
        pm25_env, pm100_env, particles_03um, particles_05um, \
        particles_10um, particles_25um, particles_50um, particles_100um  = pms5003.read_pms()
    """
    uv = si1145.read_uv
    ir = si1145.read_ir
    view = si1145.read_visible
    print('UV:         {}'.format(uv))
    print('IR:   {}'.format(ir))
    print('Visible:   {}'.format(view))

    rtc = RTC()
    #rtc.init((ds3231.DateTime(), 0, 0))
    timestamp = time.time()
    print("Timestamp: ", timestamp)

    #msg_out = struct.pack('>9HL', temp, rel_hum, co2_eq, pm25_standard, pm100_standard,
    #                    uv, ir, view, volt, timestamp)

    #send_lora_msg(msg_out)

    chrono.stop()
    lapse = chrono.read()
    print("Tiempo transcurrido: ", lapse)
    time.sleep(1)
    #https://docs.pycom.io/datasheets/development/lopy/#deep-sleep
    #machine.sleep(3600*1000)-lapse, False)
    machine.sleep(30*1000)
