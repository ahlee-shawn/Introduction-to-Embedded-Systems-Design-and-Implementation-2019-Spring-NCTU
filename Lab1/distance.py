import RPi.GPIO as GPIO
import time

v = 343
TRIGGER_PIN = 16
ECHO_PIN = 18
GPIO.setmode(GPIO.BOARD)
GPIO.setup(TRIGGER_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

def measure():
	GPIO.output(TRIGGER_PIN, GPIO.HIGH)
	time.sleep(0.00001)
	GPIO.output(TRIGGER_PIN, GPIO.LOW)

	while GPIO.input(ECHO_PIN) == GPIO.LOW:
		pulse_start = time.time()
	while GPIO.input(ECHO_PIN) == GPIO.HIGH:
		pulse_end = time.time()
	return ((pulse_end - pulse_start) * v) / 2

print measure()
GPIO.cleanup()
