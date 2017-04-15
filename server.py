#!/usr/bin/env python

"""@package docstring

This module is the server for MaRe.

Example:
    To run the WiFi Remote Car server, use the following command:

        $ python server.py

Author:
    Gary Huang<gh.nctu+code@gmail.com>

License:
    3-clause BSD License

"""

from datetime import datetime
import RPi.GPIO as GPIO
import threading
import select
import socket
import cv2
import time
import sys

class myCar:

    pwm_frequency = 200

    def __init__(self, (right1, right2), (left1, left2)):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(right1, GPIO.OUT)
        GPIO.setup(right2, GPIO.OUT)
        GPIO.setup(left1, GPIO.OUT)
        GPIO.setup(left2, GPIO.OUT)
        self.right1_pwm = GPIO.PWM(right1, self.pwm_frequency)
        self.right1_pwm.start(0.0)
        self.left1_pwm = GPIO.PWM(left1, self.pwm_frequency)
        self.left1_pwm.start(0.0)
        self.right2 = right2
        self.left2 = left2
        GPIO.output(self.right2, False)
        GPIO.output(self.left2, False)

    def rightWheel(self, value):
        if value >= 0:
            self.right1_pwm.ChangeDutyCycle(value)
            GPIO.output(self.right2, False)
        else:
            self.right1_pwm.ChangeDutyCycle(100.0 + value)
            GPIO.output(self.right2, True)

    def leftWheel(self, value):
        if value >= 0:
            self.left1_pwm.ChangeDutyCycle(value)
            GPIO.output(self.left2, False)
        else:
            self.left1_pwm.ChangeDutyCycle(100.0 + value)
            GPIO.output(self.left2, True)

    def __del__(self):
        self.left1_pwm.stop()
        self.right1_pwm.stop()


# Use BOARD numbering system
car = myCar((12, 11), (32, 31))

camera = cv2.VideoCapture(0)
camera.set(3, 320)
camera.set(4, 240)

camera_lock = threading.Lock()


class Server:

    host = ''
    port_stream = 8888
    port_control = 8889

    def __init__(self):
        self.socket_stream = None
        self.socket_control = None
        self.threads = []

    def open_socket(self):
        try:
            self.socket_stream = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_stream.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_stream.bind((self.host, self.port_stream))
            self.socket_stream.listen(5)
            self.socket_control = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_control.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket_control.bind((self.host, self.port_control))
            self.socket_control.listen(5)
            log('[INFO]', 'Server is listening on {} and {}'.format(self.port_stream, self.port_control))
        except socket.error, (value, message):
            if self.socket_stream:
                self.socket_stream.close()
            if self.socket_control:
                self.socket_control.close()
            log('[ERROR]', 'Could not open socket: ' + message)
            sys.exit(1)

    def run(self):
        self.open_socket()
        try:
            input = [self.socket_stream, self.socket_control, sys.stdin]
            running = 1
            while running:
                input_ready, output_ready, except_ready = select.select(input, [], [])

                for s in input_ready:
                    if s == self.socket_stream:
                        c = StreamClient(self.socket_stream.accept())
                        c.start()
                        self.threads.append(c)

                    elif s == self.socket_control:
                        c = ControlClient(self.socket_control.accept())
                        c.start()
                        self.threads.append(c)

                    elif s == sys.stdin:
                        cmd = sys.stdin.readline().strip()
                        if cmd == 'show':
                            s = ShowFrame()
                            s.start()
                            self.threads.append(s)
                        elif cmd == 'quit':
                            running = 0
                        elif cmd == '':
                            pass
                        else:
                            print 'Command not found: '+cmd

        except KeyboardInterrupt:
            pass

        self.socket_stream.shutdown(socket.SHUT_WR)
        self.socket_control.shutdown(socket.SHUT_WR)
        self.socket_stream.close()
        self.socket_control.close()

        for t in self.threads:
            t.running = 0
        while len(self.threads) > 0:
            self.threads = [t.join(1) for t in self.threads if t is not None and t.isAlive()]

        print 'Thank you'
        print 'If it hangs here, please press Ctrl+\\ to quit'


class ShowFrame(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.running = 1

    def run(self):
        while self.running:
            camera_lock.acquire()
            grabbed, frame = camera.read()
            camera_lock.release()
            cv2.imshow("Monitor", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            time.sleep(0.1)
        cv2.destroyWindow("Monitor")


class StreamClient(threading.Thread):

    def __init__(self, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.running = 1
        log(self.address, "connect")

    def run(self):
        try:
            while self.running:
                camera_lock.acquire()
                grabbed, frame = camera.read()
                camera_lock.release()
                jpeg = cv2.imencode('.jpg', frame)[1].tostring()
                self.client.send(jpeg)
        except socket.error as e:
            pass
        self.client.close()
        log(self.address, "close")


class ControlClient(threading.Thread):

    def __init__(self, (client, address)):
        threading.Thread.__init__(self)
        self.client = client
        self.address = address
        self.running = 1
        self.lock = threading.Lock()
        log(self.address, "connect")

    def run(self):
        try:
            while self.running:
                self.lock.acquire()
                car.rightWheel(0.0)
                car.leftWheel(0.0)
                self.lock.release()

                data = self.client.recv(64)
                if not data:
                    self.client.close()
                    self.running = 0

                cmd = ''
                for char in data:
                    if char == '\n' or char == '\r':
                        break
                    cmd += char

                pre = ''
                self.lock.acquire()
                if cmd == 'forward':
                    car.rightWheel(50.0)
                    car.leftWheel(50.0)
                    time.sleep(0.1)
                elif cmd == 'backward':
                    car.rightWheel(-100.0)
                    car.leftWheel(-100.0)
                    time.sleep(0.1)
                elif cmd == 'left':
                    car.rightWheel(24.0)
                    car.leftWheel(-24.0)
                    time.sleep(0.1)
                elif cmd == 'right':
                    car.rightWheel(-24.0)
                    car.leftWheel(24.0)
                    time.sleep(0.1)
                elif cmd == 'spring':
                    car.rightWheel(100.0)
                    car.leftWheel(100.0)
                    time.sleep(0.1)
                else:
                    pre = 'unknown '
                self.lock.release()

                log(self.address, pre+'command: '+cmd.strip())
        except socket.error as e:
            pass
        self.client.close()
        log(self.address, "close")


def log(ip, msg):
    print datetime.today().strftime('%b %d %H:%M:%S'),
    print "{} {}.".format(ip, msg)


if __name__ == '__main__':
    s = Server()
    s.run()

camera.release()
GPIO.cleanup()
