from time import sleep
import smbus
import string
import RPi.GPIO as GPIO

def getSignedNumber(number):
	if number & (1 << 15):
		return number | ~65535
	else:
		return number & 65535

LED_PIN = 12
GPIO.setmode(GPIO.BOARD)
GPIO.setup(LED_PIN, GPIO.OUT)

i2c_bus=smbus.SMBus(1)
i2c_address=0x69

i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
i2c_bus.write_byte_data(i2c_address,0x23,0x20)

while True:
	i2c_bus.write_byte(i2c_address,0x2C)
	Z_L = i2c_bus.read_byte(i2c_address)
	i2c_bus.write_byte(i2c_address,0x2D)
	Z_H = i2c_bus.read_byte(i2c_address)
	Z = Z_H << 8 | Z_L

	Z = getSignedNumber(Z)
	if Z > 500:
		GPIO.output(LED_PIN, GPIO.LOW)
	if Z < -500:
		GPIO.output(LED_PIN, GPIO.HIGH)
	sleep(0.05)
