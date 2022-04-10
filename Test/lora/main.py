from network import LoRa
import socket
import time
import ubinascii

import dht
from machine import Pin

sensor = dht.DHT22(Pin(14))

"""
# Initialise LoRa in LORAWAN mode.
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.EU868)

# create an OTAA authentication parameters
app_eui = ubinascii.unhexlify('ADA4DAE3AC12676B')
app_key = ubinascii.unhexlify('C230A4272B0D4A61916EF6D9C3F80694')
#uncomment to use LoRaWAN application provided dev_eui
#dev_eui = ubinascii.unhexlify('70B3D549938EA1EE')

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
s.send(bytes([0xcb, 0xc0, 0x09, 0xc3, 0x10, 0x71])) 


# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

# get any data received (if any...)
data = s.recv(64)
print(data)
"""

def mq135lib_example():
    """MQ135 lib example"""
    # setup
    temperature = 21.0
    humidity = 25.0

    mq135 = MQ135(0) # analog PIN 0

    # loop
    while True:
        rzero = mq135.get_rzero()
        corrected_rzero = mq135.get_corrected_rzero(temperature, humidity)
        resistance = mq135.get_resistance()
        ppm = mq135.get_ppm()
        corrected_ppm = mq135.get_corrected_ppm(temperature, humidity)

        print("MQ135 RZero: " + str(rzero) +"\t Corrected RZero: "+ str(corrected_rzero)+
              "\t Resistance: "+ str(resistance) +"\t PPM: "+str(ppm)+
              "\t Corrected PPM: "+str(corrected_ppm)+"ppm")
        time.sleep(0.3)

while True:
  try:
    sleep(2)
    sensor.measure()
    temp = sensor.temperature()
    hum = sensor.humidity()
    temp_f = temp * (9/5) + 32.0
    print('Temperature: %3.1f C' %temp)
    print('Temperature: %3.1f F' %temp_f)
    print('Humidity: %3.1f %%' %hum)
  except OSError as e:
    print('Failed to read sensor.')
