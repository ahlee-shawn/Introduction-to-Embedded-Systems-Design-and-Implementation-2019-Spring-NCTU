import schedule
import time
import picamera
import datetime

def job():
	with picamera.PiCamera() as camera:
		camera.start_preview()
		
		for i, filename in enumerate(camera.capture_continuous('image20{timestamp:%y%m%d}_{timestamp:%H%M}.jpg')):
			time.sleep(1)
			if i == 9:
				break
		camera.stop_preview()

schedule.every().day.at("14:25").do(job)
while True:
	print(datetime.datetime.now())
	schedule.run_pending()
	time.sleep(1)

