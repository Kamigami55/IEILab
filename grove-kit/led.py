import sys
import signal
import RPi.GPIO as GPIO
from IEILab.GroveStarterKit import LEDBar
from time import sleep

clk=23
dta=18

def signal_handler(signal, frame):
    GPIO.cleanup()
    print("exit!!!")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

GPIO.setmode(GPIO.BCM)
ledBar = LEDBar(clk, dta)

while True:
    ledBar.singleLed(0, 1)
    ledBar.singleLed(9, 0)
    for led in range(1, 10):
        ledBar.singleLed(led, 1)
        ledBar.singleLed(led-1, 0)
        sleep(0.1)
    for led in range(8, -1, -1):
        ledBar.singleLed(led, 1)
        ledBar.singleLed(led+1, 0)
        sleep(0.1)       

GPIO.cleanup()
