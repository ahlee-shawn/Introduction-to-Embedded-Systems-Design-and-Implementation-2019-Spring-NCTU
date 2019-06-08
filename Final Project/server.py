import sys
import os
import socket

current_x = 0
current_y = 0
current_z = 0

class Server(object):
	def __init__(self, ip, port):
		try:
			socket.inet_aton(ip)
			if 0 < int(port) < 65535:
				self.ip = ip
				self.port = int(port)
			else:
				raise Exception('Port value should between 1~65535')
			self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


		except Exception as e:
			print(e, file=sys.stderr)
			sys.exit(1)

	def run(self):
		global current_x, current_y, current_z
		self.sock.bind((self.ip, self.port))
		self.sock.listen(100)
		socket.setdefaulttimeout(0.1)
		while True:
			try:
				conn, addr = self.sock.accept()
				with conn:
					cmd = conn.recv(4096).decode()
					gear, calibrate, terminate, add_speed, minus_speed, flap, current_x, current_y, current_z = self.__process_command(cmd)
					'''if calibrate == 1:
						current_x = 0
						current_y = 0
						current_z = 0'''
					if terminate == 1:
						conn.close()
						sock.close()
						sys.exit()
			except Exception as e:
				print(e, file=sys.stderr)

	def __process_command(self, cmd):
		gear = int(cmd[0], 2)
		calibrate = int(cmd[1], 2)
		terminate = int(cmd[2], 2)
		add_speed = int(cmd[3], 2)
		minus_speed = int(cmd[4], 2)
		flap = int(cmd[5:8], 2)
		sign_x = int(cmd[8], 2)
		if sign_x == 0:
			sign_x = -1
		current_x = int(cmd[9:22], 2)
		sign_y = int(cmd[22], 2)
		if sign_y == 0:
			sign_y = -1
		current_y = int(cmd[23:36], 2)
		sign_z = int(cmd[36], 2)
		if sign_z == 0:
			sign_z = -1
		current_z = int(cmd[37:50], 2)
		os.system('clear')
		print("Gear: {}".format(gear))
		print("calibrate: {}".format(calibrate))
		print("terminate: {}".format(terminate))
		print("add_speed: {}".format(add_speed))
		print("minus_speed: {}".format(minus_speed))
		print("flap: {}".format(flap))
		print("current_x: {}".format(current_x * sign_x))
		print("current_y: {}".format(current_y * sign_y))
		print("current_z: {}".format(current_z * sign_z))
		return gear, calibrate, terminate, add_speed, minus_speed, flap, current_x * sign_x, current_y * sign_y, current_z * sign_z


def launch_server(ip, port):
	c = Server(ip, port)
	c.run()

if __name__ == '__main__':
	if sys.argv[1] and sys.argv[2]:
		launch_server(sys.argv[1], sys.argv[2])
