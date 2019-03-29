import time
import Adafruit_ADXL345
import math


accel = Adafruit_ADXL345.ADXL345()
past = 0

while True:
	time.sleep(0.5)
	x, y, z = accel.read()
	x /= 256.0
	y /= 256.0
	z /= 256.0
	acceleration = math.sqrt(x*x + y*y + z*z)
	past = 0.5 * past + 0.5 * acceleration
	print(past)
