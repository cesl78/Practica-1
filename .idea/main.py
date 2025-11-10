import cv2
import numpy as np
import os

VIDEO_PATH = "trafico.mp4"   # tu vídeo
SCALE = 0.8                    # factor de reducción
DIRECTION = "down"             # "down" (arriba->abajo) o "up" (abajo->arriba)


# ---------- 1. Cálculo del fondo: mediana de frames muestreados ----------

def calcular_fondo_median(video_path, n_samples=60, scale=1.0):
    print("Directorio actual:", os.getcwd())
    print("Usando VIDEO_PATH:", os.path.abspath(video_path))

    if not os.path.exists(video_path):
        print("No se encuentra el archivo de vídeo. Revisa el nombre o la ruta.")
        return None, None, None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("OpenCV no ha podido abrir el vídeo.")
        return None, None, None

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    if total_frames <= 0:
        print("El vídeo no tiene frames válidos.")
        cap.release()
        return None, None, None

    indices = np.linspace(0, total_frames - 1, n_samples, dtype=int)

    frames = []
    alto = ancho = None

    for idx in indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
        ret, frame = cap.read()
        if not ret:
            continue

        if scale != 1.0:
            frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

        if alto is None:
            alto, ancho, _ = frame.shape

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)
        frames.append(gray.astype(np.float32))

    cap.release()

    if len(frames) == 0:
        print("No se han podido leer frames para calcular el fondo.")
        return None, None, None

    stack = np.stack(frames, axis=0)
    fondo_median = np.median(stack, axis=0).astype(np.uint8)
    print("Frames usados para el fondo (muestras reales):", len(frames))

    return fondo_median, alto, ancho


# ---------- 2. Clase Track para cada coche ----------

class Track:
    def __init__(self, track_id, cx, cy):
        self.id = track_id
        self.cx = cx
        self.cy = cy
        self.last_cy = cy
        self.counted = False
        self.missed = 0


def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


# ---------- 3. Detección + tracking + conteo ----------

def detectar_y_contar(video_path, fondo, alto, ancho, scale=1.0, direction="down"):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("OpenCV no ha podido abrir el vídeo.")
        return

    area_total = alto * ancho

    # parámetros detección
    area_min_frac = 0.00015
    area_min = area_total * area_min_frac
    roi_y_min_frac = 0.25
    roi_y_max_frac = 1.0
    roi_y_min = int(alto * roi_y_min_frac)
    roi_y_max = int(alto * roi_y_max_frac)

    # línea virtual de conteo (puedes mover el 0.6)
    line_y_frac = 0.6
    line_y = int(alto * line_y_frac)

    # parámetros tracking
    max_dist = 50
    max_missed = 10

    tracks = []
    next_id = 0
    conteo = 0

    while True:
        ret, frame_color = cap.read()
        if not ret:
            break

        if scale != 1.0:
            frame_color = cv2.resize(frame_color, (0, 0), fx=scale, fy=scale)

        gray = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (7, 7), 0)

        diff = cv2.absdiff(gray, fondo)
        _, thresh = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)

        # ROI interna (no dibujamos la línea en el vídeo final)
        mask_roi = np.zeros_like(thresh)
        mask_roi[roi_y_min:roi_y_max, :] = 255
        thresh = cv2.bitwise_and(thresh, mask_roi)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=2)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)

        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detecciones = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < area_min:
                continue

            x, y, w, h = cv2.boundingRect(cnt)
            cx = x + w // 2
            cy = y + h // 2
            detecciones.append((x, y, w, h, cx, cy))

        # --- tracking ---

        for t in tracks:
            t.missed += 1

        for (x, y, w, h, cx, cy) in detecciones:
            mejor_track = None
            mejor_dist = max_dist

            for t in tracks:
                d = distancia((cx, cy), (t.cx, t.cy))
                if d < mejor_dist:
                    mejor_dist = d
                    mejor_track = t

            if mejor_track is not None:
                mejor_track.last_cy = mejor_track.cy
                mejor_track.cx = cx
                mejor_track.cy = cy
                mejor_track.missed = 0
            else:
                nuevo = Track(next_id, cx, cy)
                tracks.append(nuevo)
                next_id += 1

        tracks = [t for t in tracks if t.missed <= max_missed]

        # --- conteo ---

        for t in tracks:
            if t.counted:
                continue

            if direction == "down":
                if t.last_cy < line_y <= t.cy:
                    t.counted = True
                    conteo += 1
            else:  # "up"
                if t.last_cy > line_y >= t.cy:
                    t.counted = True
                    conteo += 1

        # --- dibujar resultado ---

        frame_draw = frame_color.copy()

        for (x, y, w, h, cx, cy) in detecciones:
            cv2.rectangle(frame_draw, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame_draw, (cx, cy), 3, (0, 0, 255), -1)

        for t in tracks:
            cv2.circle(frame_draw, (int(t.cx), int(t.cy)), 4, (0, 255, 255), -1)
            cv2.putText(frame_draw, f"ID {t.id}",
                        (int(t.cx) + 5, int(t.cy) - 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                        (0, 255, 255), 1)

        # Línea de conteo (si no quieres verla, comenta estas dos líneas)
        cv2.line(frame_draw, (0, line_y), (ancho, line_y), (255, 0, 0), 2)

        cv2.putText(frame_draw, f"Conteo: {conteo}",
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0,
                    (0, 0, 255), 2)

        cv2.imshow("Mascara", thresh)
        cv2.imshow("Deteccion + conteo", frame_draw)

        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Total de vehiculos contados:", conteo)


# ---------- 4. Main ----------

def main():
    fondo, alto, ancho = calcular_fondo_median(VIDEO_PATH, n_samples=60, scale=SCALE)
    if fondo is None:
        return

    detectar_y_contar(VIDEO_PATH, fondo, alto, ancho, scale=SCALE, direction=DIRECTION)


if __name__ == "__main__":
    main()