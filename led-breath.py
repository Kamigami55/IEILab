import RPi.GPIO as GPIO 
import time

GPIO.setmode(GPIO.BOARD)
ledPin = 12
GPIO.setup(ledPin, GPIO.OUT)
pwm = GPIO.PWM(ledPin, 100)
pwm.start(100)

while True:
    for duty in range(100, 0, -10):
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.1)
    for duty in range(0, 100, 10):
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.1)
    
