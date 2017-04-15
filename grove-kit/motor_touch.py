import RPi.GPIO as GPIO
from IEILab.GroveStarterKit import TouchSensor, Servo
import time
from time import sleep

touchpin = 18
servopin = 23
dir = 1

#debounce touch
DEBOUNCE_DELAY = 0.05
btnState = 0
rawBtnIn = 0
prevBtnIn = 0  
lastDebounceTime = 0

GPIO.setmode(GPIO.BCM)

touch = TouchSensor()
touch.attach(touchpin)

servo = Servo()
servo.attach(servopin)

angle = 130
print(angle)
servo.write(angle)


def buttonPressed():
    global dir
    global angle
    if(dir == 0): # left
        if(angle < 10):
            angle = 0
            dir = 1
        else:
            angle = angle - 10
    else: # right
        if(angle > 160):
            angle = 180
            dir = 0
        else:
            angle = angle + 20
    servo.write(angle)
    print(angle)
   

def updateButtonState():
    global rawBtnIn
    global btnState
    global lastDebounceTime
    global prevBtnIn
    prevBtnIn = rawBtnIn # rawBtnIn now is still previous
    rawBtnIn = touch.isTouched()
    if (rawBtnIn != prevBtnIn):
        lastDebounceTime = time.clock()
    elif ((time.clock() - lastDebounceTime) > DEBOUNCE_DELAY): # steady
        if (rawBtnIn != btnState): # button state has changed
            btnState = rawBtnIn
            if (btnState == 1): # Button Pressed
                buttonPressed()


try:
    while True:
        updateButtonState()

except KeyboardInterrupt:
    pass

print("exit")
GPIO.cleanup()
