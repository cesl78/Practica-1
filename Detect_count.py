import cv2
import numpy as np


# --- CLASE TRACK ---
class Track:
    def __init__(self, track_id, cx, cy):
        self.id = track_id
        self.cx = cx
        self.cy = cy
        self.last_cy = cy
        self.start_cy = cy
        self.counted = False
        self.missed = 0
        self.visible_frames = 1


def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))


# --- CLASE VEHICLECOUNTER ---
class VehicleCounter:
    def __init__(self, video_path, background, height, width, scale=1.0, direction="down"):
        self.video_path = video_path
        self.background = background
        self.height = height
        self.width = width
        self.scale = scale
        self.direction = direction

        # ---------------- PARÁMETROS OPTIMIZADOS ----------------
        self.area_min_frac = 0.00012  # 🔧 Bajado ligeramente para no perder vehículos pequeños
        self.max_dist = 65  # 🔧 Más margen para el tracking
        self.max_missed = 20  # 🔧 Más tolerancia a desapariciones temporales
        self.min_visible_frames = 2  # 🔧 Bajado a 2 para detectar vehículos rápidos/fugaces

        # ---------------- ZONA VÁLIDA ----------------
        self.x_min = int(self.width * 0.05)
        self.x_max = int(self.width * 0.55)
        self.y_min = int(self.height * 0.35)  # 🔧 Ampliada zona de detección
        self.y_max = int(self.height * 0.85)

        self.tracks = []
        self.next_id = 0
        self.cnt_up = 0
        self.cnt_down = 0
        self.conteo = 0

    def _en_carriles_validos(self, cx, cy):
        return (self.x_min <= cx <= self.x_max) and (self.y_min <= cy <= self.y_max)

    def _procesar_frame(self, frame_color):
        gray = cv2.cvtColor(frame_color, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        diff = cv2.absdiff(gray, self.background)

        # 🔧 Umbral intermedio para no perder nitidez ni objetos
        _, thresh = cv2.threshold(diff, 22, 255, cv2.THRESH_BINARY)

        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        # Limpieza suave
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=1)
        thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)

        return thresh

    def run(self):
        cap = cv2.VideoCapture(self.video_path)
        area_min = (self.height * self.width) * self.area_min_frac

        # 🔧 Definimos límites para "objetos múltiples"
        ancho_max_coche = int(self.width * 0.12)  # Ajustar según el vídeo
        alto_max_coche = int(self.height * 0.15)

        while True:
            ret, frame_color = cap.read()
            if not ret: break

            if self.scale != 1.0:
                frame_color = cv2.resize(frame_color, (0, 0), fx=self.scale, fy=self.scale)

            thresh = self._procesar_frame(frame_color)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            detecciones = []
            for cnt in contours:
                if cv2.contourArea(cnt) < area_min: continue

                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w // 2, y + h // 2

                if not self._en_carriles_validos(cx, cy): continue

                # 🔧 LÓGICA DE DIVISIÓN DINÁMICA
                # Si es muy ancho (posibles 2 coches en paralelo)
                if w > ancho_max_coche * 1.8:
                    detecciones.append((x, y, w // 2, h, cx - w // 4, cy))
                    detecciones.append((x + w // 2, y, w // 2, h, cx + w // 4, cy))
                # Si es muy alto (posibles 2 coches uno tras otro)
                elif h > alto_max_coche * 1.8:
                    detecciones.append((x, y, w, h // 2, cx, cy - h // 4))
                    detecciones.append((x, y + h // 2, w, h // 2, cx, cy + h // 4))
                else:
                    detecciones.append((x, y, w, h, cx, cy))

            # --- Actualización de Tracks ---
            for t in self.tracks: t.missed += 1

            for (x, y, w, h, cx, cy) in detecciones:
                mejor_track = None
                mejor_dist = self.max_dist
                for t in self.tracks:
                    d = distancia((cx, cy), (t.cx, t.cy))
                    if d < mejor_dist:
                        mejor_dist = d
                        mejor_track = t

                if mejor_track is not None:
                    mejor_track.cx, mejor_track.cy = cx, cy
                    mejor_track.missed = 0
                    mejor_track.visible_frames += 1
                else:
                    nuevo = Track(self.next_id, cx, cy)
                    self.tracks.append(nuevo)
                    self.next_id += 1

            self.tracks = [t for t in self.tracks if t.missed <= self.max_missed]

            # --- Conteo ---
            for t in self.tracks:
                if not t.counted and t.visible_frames >= self.min_visible_frames:
                    desplazamiento = t.cy - t.start_cy
                    # Filtro de movimiento mínimo para evitar ruidos fijos
                    if abs(desplazamiento) > 5 or t.visible_frames > 5:
                        t.counted = True
                        if desplazamiento > 0:
                            self.cnt_down += 1
                        else:
                            self.cnt_up += 1
                        self.conteo += 1

            # --- Visualización ---
            for (x, y, w, h, cx, cy) in detecciones:
                cv2.rectangle(frame_color, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # --- Mostrar contadores ---
            # Total
            cv2.putText(frame_color, f"Total: {self.conteo}", (50, 50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 255), 3)
            # Suben
            cv2.putText(frame_color, f"Suben: {self.cnt_up}", (50, 100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 50, 50), 3)
            # Bajan
            cv2.putText(frame_color, f"Bajan: {self.cnt_down}", (50, 150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1.2, (50, 50, 255), 3)

            cv2.imshow("Deteccion Final", frame_color)
            if cv2.waitKey(1) & 0xFF == 27: break

        cap.release()
        cv2.destroyAllWindows()
        print(f"Resultado final -> Total: {self.conteo}, Suben: {self.cnt_up}, Bajan: {self.cnt_down}")