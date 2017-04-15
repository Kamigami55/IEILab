import cv2
camera = cv2.VideoCapture(0)

# Define the codec and create VideoWriter object
fourcc = cv2.cv.CV_FOURCC(*'XVID')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

while(camera.isOpened()):
    ret, frame = camera.read()
    if ret == True:
        # write the frame
        out.write(frame)
        cv2.imshow('Record Video',frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    else:
        break

camera.release()
out.release()
cv2.destroyAllWindows()
