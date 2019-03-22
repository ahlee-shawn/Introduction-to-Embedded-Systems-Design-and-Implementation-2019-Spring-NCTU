import time
import Adafruit_ADXL345
import RPi.GPIO as GPIO
import math

LED_PIN = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

accel = Adafruit_ADXL345.ADXL345()
prev = 0.0
var = 0.01
time_past = 0

while True:
	x, y, z = accel.read()
	x /= 256.0
	y /= 256.0
	z /= 256.0
	temp = math.sqrt(x * x + y * y + z * z)
	if abs(temp - prev) > var:
		GPIO.output(LED_PIN, GPIO.LOW)
		time_past = 0
	else:
		if time_past < 10:
			time_past += 1
	if time_past >= 10:
		GPIO.output(LED_PIN, GPIO.HIGH)
	prev = temp
	time.sleep(0.5)
