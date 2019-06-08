import RPi.GPIO as GPIO
import sys 
import time
import smbus
import socket
import threading

Gear = 15
Calibrate = 38
Terminate = 40
Flap_Button_Up = 7
Flap_Button_Down = 12
Speed_Up = 11
Speed_Down = 13

X = 0.0
Y = 0.0
Z = 0.0
x = 0
y = 0
z = 0
gear = 1
benchmark_x = 0.0
benchmark_y = 0.0
benchmark_z = 0.0
current_flap = 0
terminate = 0
current_x = 0.0
current_y = 0.0
current_z = 0.0

def GEAR(channel):
	global gear
	gear = int(gear == 0)

def ADD_FLAP(channel):
	global current_flap
	if current_flap < 5:
		current_flap += 1

def MINUS_FLAP(channel):
	global current_flap
	if current_flap > 0:
		current_flap -= 1

def CALIBRATE(channel):
	global benchmark_x, benchmark_y, benchmark_z, X, Y, Z, current_x, current_y, current_z, x, y, z
	current_x = 0.0
	current_y = 0.0
	current_z = 0.0
	x = 0
	y = 0
	z = 0
	temp = [0.0, 0.0, 0.0]
	for i in range(0, 100):
		a, b ,c = get_gyro()
		temp[0] += a
		temp[1] += b
		temp[2] += c
	temp[0] /= 100
	temp[1] /= 100
	temp[2] /= 100
	benchmark_x = temp[0]
	benchmark_y = temp[1]
	benchmark_z = temp[2]

def TERMINATE(channel):
	global terminate
	terminate = 1

GPIO.setmode(GPIO.BOARD)
GPIO.setup(Gear, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Gear, GPIO.FALLING, callback=GEAR, bouncetime=250)
GPIO.setup(Flap_Button_Up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Flap_Button_Up, GPIO.FALLING, callback=ADD_FLAP, bouncetime=250)
GPIO.setup(Flap_Button_Down, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Flap_Button_Down, GPIO.FALLING, callback=MINUS_FLAP, bouncetime=250)
GPIO.setup(Calibrate, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Calibrate, GPIO.FALLING, callback=CALIBRATE, bouncetime=250)
GPIO.setup(Terminate, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.add_event_detect(Terminate, GPIO.FALLING, callback=TERMINATE, bouncetime=250)
GPIO.setup(Speed_Up, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(Speed_Down, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def getSignedNumber(number):
	if int(number) & (1 << 15):
		return int(number) | ~65535
	else:
		return int(number) & 65535

def get_gyro():
	global X, Y, Z
	i2c_bus.write_byte(i2c_address,0x28)
	X_L = i2c_bus.read_byte(i2c_address)
	i2c_bus.write_byte(i2c_address,0x29)
	X_H = i2c_bus.read_byte(i2c_address)
	X = X_H << 8 | X_L

	i2c_bus.write_byte(i2c_address,0x2A)
	Y_L = i2c_bus.read_byte(i2c_address)
	i2c_bus.write_byte(i2c_address,0x2B)
	Y_H = i2c_bus.read_byte(i2c_address)
	Y = Y_H << 8 | Y_L

	i2c_bus.write_byte(i2c_address,0x2C)
	Z_L = i2c_bus.read_byte(i2c_address)
	i2c_bus.write_byte(i2c_address,0x2D)
	Z_H = i2c_bus.read_byte(i2c_address)
	Z = Z_H << 8 | Z_L

	X = getSignedNumber(X) * 70 / 1000
	Y = getSignedNumber(Y) * 70 / 1000
	Z = getSignedNumber(Z) * 70 / 1000
	return X, Y, Z

class Client(object):
	def __init__(self, ip, port):
		try:
			socket.inet_aton(ip)
			if 0 < int(port) < 65535:
				self.ip = ip
				self.port = int(port)
			else:
				raise Exception('Port value should between 1~65535')
		except Exception as e:
			print(e, file=sys.stderr)
			sys.exit(1)

	def run(self):
		global current_x, current_y, current_z, x, y, z
		while True:
			start = time.time()
			x, y, z = get_gyro()
			x -= benchmark_x
			y -= benchmark_y
			z -= benchmark_z
			calibrate = int(GPIO.input(Calibrate) == GPIO.LOW)
			add_speed = int(GPIO.input(Speed_Up) == GPIO.LOW)
			minus_speed = int(GPIO.input(Speed_Down) == GPIO.LOW)
			if x <= 3 and x >= -3:
				x = 0
			if y <= 3 and y >= -3:
				y = 0
			if z <= 3 and z >= -3:
				z = 0
			current_x += (x * 0.1)
			current_y += (y * 0.1)
			current_z += (z * 0.1)
			sign_x = int(current_x > 0)
			sign_y = int(current_y > 0)
			sign_z = int(current_z > 0)
			if current_x < 0:
				x = -1 * current_x
			else:
				x = current_x
			if current_y < 0:
				y = -1 * current_y
			else:
				y = current_y
			if current_z < 0:
				z = -1 * current_z
			else:
				z = current_z
			msg = format(int(gear), '01b') + format(int(calibrate), '01b') + format(int(terminate), '01b') + format(int(add_speed), '01b') + format(int(minus_speed), '01b') + format(int(current_flap), '03b') + format(int(sign_x), '01b') + format(int(x), '013b') + format(int(sign_y), '01b') + format(int(y), '013b') + format(int(sign_z), '01b') + format(int(z), '013b')
			with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
				s.connect((self.ip, self.port))
				s.send(msg.encode())
			if terminate == 1:
				GPIO.cleanup()
				sys.exit(1)
			time_past = time.time() - start
			time_to_sleep = 0.1 - time_past
			if time_to_sleep > 0:
				time.sleep(time_to_sleep)
			else:
				print(time_to_sleep)

def launch_client(ip, port):
	c = Client(ip, port)
	c.run()

if __name__ == "__main__":
	i2c_bus=smbus.SMBus(1)
	i2c_address=0x69
	i2c_bus.write_byte_data(i2c_address,0x20,0x0F)
	i2c_bus.write_byte_data(i2c_address,0x23,0x20)
	if len(sys.argv) == 3:
		launch_client(sys.argv[1], sys.argv[2]) #IP, Port
	else:
		print('Usage: python3 {} IP PORT'.format(sys.argv[0]))