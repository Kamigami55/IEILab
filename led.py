import RPi.GPIO as GPIO 
import time

GPIO.setmode(GPIO.BOARD)
ledPin = 12
GPIO.setup(ledPin, GPIO.OUT)

while True:
    GPIO.output(ledPin, True)
    time.sleep(0.5)
    GPIO.output(ledPin, False)
    time.sleep(0.5)

