import picamera
import time

with picamera.PiCamera() as camera:
	camera.resolution = (640,480)
	camera.framerate = 24
	camera.start_preview()
	camera.annotate_text = str(int(time.time()))
	time.sleep(2)
	camera.capture("foo.jpg")