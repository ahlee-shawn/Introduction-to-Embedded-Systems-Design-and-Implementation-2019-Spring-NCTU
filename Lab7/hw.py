import speech_recognition as sr
import sys
import Adafruit_DHT
from gtts import gTTS
import os

sensor_args = { '11': Adafruit_DHT.DHT11,
				'22': Adafruit_DHT.DHT22,
				'2302': Adafruit_DHT.AM2302}

sensor = sensor_args[sys.argv[1]]
pin = sys.argv[2]

#obtain audio from the microphone
r=sr.Recognizer()

with sr.Microphone() as source:
	print("Please wait. Calibrating microphone...")
	#listen for 1 seconds and create the ambient noise energy level
	r.adjust_for_ambient_noise(source, duration=1)
	print("Say something!")
	audio=r.listen(source)
# recognize speech using Google Speech Recognition

try:
	print("Google Speech Recognition thinks you said:")
	print(r.recognize_google(audio))
	if r.recognize_google(audio).split(" ")[1] == "test":
		humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
		temp = "The temperature is " + str(temperature) + ". The humidity is " + str(humidity)
		print(temp)
		tts = gTTS(text=temp, lang='en')
		tts.save('test.mp3')
		os.system('omxplayer -o local -p test.mp3')
	exit(1)
except sr.UnknownValueError:
	print("Google Speech Recognition could not understand audio")
except sr.RequestError as e:
	print("No response from Google Speech Recognition service: {0}".format(e))