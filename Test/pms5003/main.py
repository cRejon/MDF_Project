import pms5003
import machine
import time


print("Initing UART")
uart = machine.UART(1, 9600, parity=None, stop=1, pins=('P15','P14'))
time.sleep(30)
print("Initing PMS5003")
pms = pms5003.PMS5003(uart, set='P17', reset='P16')
pms.set_pms()
pm10_standard, pm25_standard, pm100_standard, pm10_env, \
    pm25_env, pm100_env, particles_03um, particles_05um, \
    particles_10um, particles_25um, particles_50um, particles_100um  = pms.read_pms()
