import RPi.GPIO as GPIO
import time

v = 343
LED_PIN = 12
TRIGGER_PIN = 16
ECHO_PIN = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)

def measure():
	GPIO.output(TRIGGER_PIN, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(TRIGGER_PIN, GPIO.LOW)

	while GPIO.input(ECHO_PIN) == GPIO.LOW:
		pulse_start = time.time()
	while GPIO.input(ECHO_PIN) == GPIO.HIGH:
		pulse_end = time.time()
	distance = ((pulse_end - pulse_start) * v) / 2
	if distance >= 1:
		GPIO.output(LED_PIN, GPIO.LOW)
		return
	elif distance <= 0.3:
		GPIO.output(LED_PIN, GPIO.HIGH)
		time.sleep(0.1)
		GPIO.output(LED_PIN, GPIO.LOW)
		time.sleep(0.1)
		return
	else:
		GPIO.output(LED_PIN, GPIO.HIGH)
		time.sleep(0.5)
		GPIO.output(LED_PIN, GPIO.LOW)
		time.sleep(0.5)
		return

try:
	while True:
		measure()
except KeyboardInterrupt:
	print("Exception: KeyboardInterrupt")
finally:
	GPIO.cleanup()
