# @file GroveStarterKit.py
#
# Grove Starter Kit for LinkIt ONE on IEILab course
#
# @author Gary <gh.nctu+code@gmail.com>
import RPi.GPIO as GPIO
import time


class DHT:

    MAXTIMINGS = 85

    def __init__(self, pin):
        self._pin = pin
        self.firstreading = True

    def begin(self):
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, True)
        self._lastreadtime = 0

    def readHT(self):
        laststate = True
        counter = 0

        # Pull the pin high and wait 250 millisecond
        GPIO.output(self._pin, True)
        time.sleep(0.25)

        currenttime = millis()
        if currenttime < self._lastreadtime:
            # there was a rollover
            self._lastreadtime = 0

        if not self.firstreading and (currenttime - self._lastreadtime) < 2000:
            # return last correct measurement
            return (self.temp, self.humi)

        self.firstreading = False
        self._lastreadtime = millis()

        data = [0] * 5

        # Now pull it low for 20 milliseconds
        GPIO.setup(self._pin, GPIO.OUT)
        GPIO.output(self._pin, False)
        time.sleep(0.02)
        GPIO.output(self._pin, True)
        time.sleep(40e-6)
        GPIO.setup(self._pin, GPIO.IN)

        count_buf = []
        count_len = 0
        j = 0
        for i in range(self.MAXTIMINGS):

            counter = 0

            while True:
                state = bool(GPIO.input(self._pin)) 
                #print int(state),
                if state != laststate:
                    break
                counter += 1
                if counter == 100:
                    break
            #print

            count_buf.append(counter)
            laststate = bool(GPIO.input(self._pin))

            if counter == 100:
                break

            if i >= 4 and i % 2 == 0:
                data[j / 8] <<= 1;
                if counter > 6:
                    data[j / 8] |= 1
                j += 1

        # end for

        f = float(data[2] & 0x7F)
        f *= 256.0
        f += data[3]
        f /= 20.0
        if data[2] & 0x80:
            f *= -1

        if f > 15.0 and f < 40.0:
            self.temp = f
            f = float(data[0])
            f *= 256.0
            f += data[1]
            f /= 20.0
            self.humi = f
            GPIO.setup(self._pin, GPIO.OUT)
            return (self.temp, self.humi)

        GPIO.setup(self._pin, GPIO.OUT)
        return ()


class DustSensor:
    pass


class LEDBar:

    CMDMODE = 0x0000
    ON      = 0x00ff
    SHUT    = 0x0000

    def __init__(self, clk, dta):
        GPIO.setup(clk, GPIO.OUT)
        GPIO.setup(dta, GPIO.OUT)
        self.clk = clk
        self.dta = dta
        self.led_state = 0

    def setLevel(self, level):

        if level > 10:
            raise ValueError('level is out of range')

        # Build and send the packet
        self.__send16bitData(self.CMDMODE)
        for i in range(12):
            state = self.ON if i < level else self.SHUT
            self.__send16bitData(state)
        self.__latchData()

    def setLevelReverse(self, level):

        if level > 10:
            raise ValueError('level is out of range')

        # Build and send the packet
        self.__send16bitData(self.CMDMODE)
        for i in range(12):
            state = self.ON if i >= (10 - level) else self.SHUT
            self.__send16bitData(state)
        self.__latchData()
        pass

    def indexBit(self, index_bits):
        self.__send16bitData(self.CMDMODE)
        for i in range(12):
            state = self.ON if index_bits & 0x0001 else self.SHUT
            self.__send16bitData(state)
            index_bits >>= 1
        self.__latchData()

    def singleLed(self, num, state):
        if num > 10:
            raise ValueError('num is out of range')
        self.led_state = (self.led_state | (0x01 << num)) if state \
                else (self.led_state & ~(0x01 << num));
        self.indexBit(self.led_state)

    def __send16bitData(self, data):
        for i in range(16):
            state = True if data & 0x8000 else False
            GPIO.output(self.dta, state)
            state = False if GPIO.input(self.clk) else True
            GPIO.output(self.clk, state)
            data <<= 1

    def __latchData(self):
        GPIO.output(self.dta, False)
        time.sleep(1e-5)
        for i in range(4):
            GPIO.output(self.dta, True)
            GPIO.output(self.dta, False)


class LightSensor:

    def __init__(self):
        print 'Sorry, there\'s no analog inputs on GPIOs'


class Servo:
    # If you double the PWM freqnency, you also have to double the three
    # pulse width parameters
    REFRESH_FREQUENCY   = 50
    MIN_PULSE_WIDTH     =  2.72     #   0 degrees: 0.544 ms
    DEFAULT_PULSE_WIDTH =  7.50     #  90 degrees: 1.500 ms
    MAX_PULSE_WIDTH     = 12.00     # 180 degrees: 2.400 ms

    def __init__(self):
        self._angle = 0.0
        self._value = 0
        self._attached = False

    def attach(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, self.REFRESH_FREQUENCY)
        self.pwm.start(self.DEFAULT_PULSE_WIDTH)
        self._pin = pin
        self._attached = True
        time.sleep(0.01)    # destroy the signal

    def write(self, angle):
        if not self._attached:
            raise ValueError('Not attach yet')
        if int(angle) < 0 or int(angle) > 180:
            raise ValueError('angle is out of range')
        self._angle = angle
        rang = 180.0 / (self.MAX_PULSE_WIDTH - self.MIN_PULSE_WIDTH)
        duty = float(angle) / rang + self.MIN_PULSE_WIDTH
        self.pwm.ChangeDutyCycle(duty)

    def read(self):
        if not self._attached:
            raise ValueError('Not attach yet')
        return self._angle

    def attached(self):
        return self._attached

    def detach(self):
        if not self._attached:
            raise ValueError('Not attach yet')
        self.pwm.stop()
        self._attached = False

    def __del__(self):
        self.detach()


class SoundSensor:

    def __init__(self):
        print 'Sorry, there\'s no analog inputs on GPIOs'


class TouchSensor:

    def __init__(self):
        self._attached = False

    def attach(self, pin):
        GPIO.setup(pin, GPIO.IN)
        self._pin = pin
        self._attached = True

    def isTouched(self):
        if not self._attached:
            raise ValueError('Not attach yet')
        return GPIO.input(self._pin)

    def attached(self):
        return self._attached

    def detach(self):
        if not self._attached:
            raise ValueError('Not attach yet')
        self._attached = False


class UVSensor:

    def __init__(self):
        print 'Sorry, there\'s no analog inputs on GPIOs'

    #def show(self):
    #    for i in range(32):
    #        sensorValue = # 10-bit ADC outputs
    #        sum = sensorValue + sum
    #        time.sleep(0.001)
    #    sum >>= 5
    #    print 'The voltage value:'
    #    print '{:%f}mV'.format(sum * 4980.0 / 1023.0)


def millis():
    return int(round(time.time() * 1000.0))



