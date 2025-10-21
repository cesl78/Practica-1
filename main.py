import cv2

cap = cv2.VideoCapture("trafico.mp4")

while (1):

    _, frame = cap.read()
    frame = cv2.resize(frame, (400, 300))

    cv2.imshow('original', frame)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

cap.release()