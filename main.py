import cv2

cap = cv2.VideoCapture(r"C:\Users\cesar\Desktop\UNI\2025-2026\2025\FSI\Trabajos\Radar\tráfico01.mp4")

while (1):

    # Take each frame
    _, frame = cap.read()
    frame = cv2.resize(frame, (400, 300))

    cv2.imshow('original', frame)

    k = cv2.waitKey(5) & 0xFF
    if k == 27:
        break

cv2.destroyAllWindows()

cap.release()