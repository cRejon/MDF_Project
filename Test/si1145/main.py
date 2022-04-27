# LoPy simple teste
from machine import I2C
import si1145
import time
i2c = I2C(0)
i2c.init(I2C.MASTER, baudrate=100000, pins=('P22','P23'))
sensor = si1145.SI1145(i2c=i2c)
while True:
    uv = sensor.read_uv
    ir = sensor.read_ir
    view = sensor.read_visible
    print(" UV: %f\n IR: %f\n Visible: %f" % (uv, ir, view))
    time.sleep(10)
