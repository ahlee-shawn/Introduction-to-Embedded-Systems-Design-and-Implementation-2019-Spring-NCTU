import sys
import Adafruit_DHT
import RPi.GPIO as GPIO
import time

LED_PIN = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

sensor_args = { '11': Adafruit_DHT.DHT11,
				'22': Adafruit_DHT.DHT22,
				'2302': Adafruit_DHT.AM2302,}

if len(sys.argv) == 4 and sys.argv[1] in sensor_args:
	sensor = sensor_args[sys.argv[1]]
	pin = sys.argv[2]
	temp = float(sys.argv[3])
else:
	print('usage: sudo ./Adafruit_DHT.py [11|22|2302] GPIOpin#')
	print('example: sudo ./Adafruit_DHT.py 2302 4 - Read from an AM2302 connected to GPIO #4')
	GPIO.cleanup()
	sys.exit(1)

try:
	while True:
		humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
		if temperature is not None:
			if float(temperature) > temp:
				GPIO.output(LED_PIN, GPIO.HIGH)
			else:
				GPIO.output(LED_PIN, GPIO.LOW)
		else:
			print('Failed to get reading. Try again!') 
			GPIO.cleanup()
			sys.exit(1)
except KeyboardInterrupt:
	print("Exception: KeyboardInterrupt")
finally:
	GPIO.cleanup()
