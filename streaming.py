import cv2
import numpy as np

camera = cv2.VideoCapture(0)
camera.set(3, 320) # width (max for c170: 640)
camera.set(4, 240) # height (max for c170: 480)

while True:
    grabbed, frame = camera.read()
    rframe = frame.copy()
    rframe = cv2.flip(frame, 1)
    cv2.imshow('Webcam Streaming', frame)
    cv2.imshow('Webcam Streaming2', rframe)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()
cv2.destroyAllWindows()
