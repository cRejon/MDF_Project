import time
import si7021
from machine import I2C

i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))

def run_example():
    '''Runs all of the methods from the i2c driver. Imports are included in the
    method for re-importing any updates when testing.
    '''
    temp_sensor = si7021.Si7021(i2c)
    print('Serial:              {value}'.format(value=temp_sensor.serial))
    print('Identifier:          {value}'.format(value=temp_sensor.identifier))
    print('Temperature:         {value}'.format(value=temp_sensor.temperature))
    print('Relative Humidity:   {value}'.format(value=temp_sensor.relative_humidity))

    temp_sensor.reset()
    print('\nModule reset.\n')

    print('Temperature:         {value}'.format(value=temp_sensor.temperature))
    print('Relative Humidity:   {value}'.format(value=temp_sensor.relative_humidity))

    print('Fahrenheit:          {value}'.format(
        value=si7021.convert_celcius_to_fahrenheit(temp_sensor.temperature)))

while True:
    addrs = i2c.scan()
    print('Direcciones:  {value}'.format(value=addrs))
    run_example()
    time.sleep(5)
