import cv2

video = cv2.VideoCapture('output.avi')
while video.isOpened():
    ret, frame = video.read()

    if ret == False:
        break
    
    cv2.imshow('Play Video', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
