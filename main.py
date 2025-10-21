import cv2

VIDEO_CAPTURE = cv2.VideoCapture("C:\Users\cesar\Desktop\UNI\2025-2026\2025\FSI\Trabajos\Radar\tráfico01.mp4")
import numpy as np

cap = VIDEO_CAPTURE

while (1):

    # Take each frame
    _, frame = cap.read()
    frame = cv2.resize(frame, (400, 300))


    # Calculation of Sobelx uvyv
    sobel = cv2.Sobel(frame, cv2.CV_8U, 1, 1, ksize=3)

    cv2.imshow('original', frame)
    cv2.imshow('sobel', sobel)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

cap.release()