import cv2
import numpy as np
import os

# Nombre del archivo donde se guardará el fondo promedio.
BACKGROUND_IMAGE_NAME = "average_background.png"


class Background:

    def __init__(self, video_path, n_samples=60, scale=1.0):
        self.video_path = video_path
        self.n_samples = n_samples
        self.scale = scale
        self.image, self.height, self.width = self._cargar_o_calcular_fondo()

    def _guardar_fondo(self):
        """Guarda la imagen del fondo promedio en el disco."""
        cv2.imwrite(BACKGROUND_IMAGE_NAME, self.image)
        print(f"Fondo promedio guardado como: {BACKGROUND_IMAGE_NAME}")

    def _get_expected_dimensions(self):
        """Calcula las dimensiones HxW esperadas de un fotograma escalado."""
        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise RuntimeError(f"No se pudo abrir el video en: {self.video_path}")

        # PROPIEDADES CORREGIDAS
        original_w = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        original_h = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        cap.release()

        expected_w = int(original_w * self.scale)
        expected_h = int(original_h * self.scale)

        return expected_h, expected_w

    def _cargar_o_calcular_fondo(self):
        """Intenta cargar el fondo; si no existe o es incompatible, lo calcula y lo guarda."""

        expected_h, expected_w = self._get_expected_dimensions()

        # 1. INTENTAR CARGAR
        if os.path.exists(BACKGROUND_IMAGE_NAME):
            print(f"Intentando cargar fondo promedio desde: {BACKGROUND_IMAGE_NAME}")
            loaded_image = cv2.imread(BACKGROUND_IMAGE_NAME, cv2.IMREAD_GRAYSCALE)

            if loaded_image is not None:
                alto, ancho = loaded_image.shape

                # 2. VERIFICAR COMPATIBILIDAD
                if alto == expected_h and ancho == expected_w:
                    print("Fondo cargado exitosamente. Saltando cálculo.")
                    return loaded_image, alto, ancho
                else:
                    print(f"ERROR: Fondo incompatible. Esperado {expected_h}x{expected_w}, Cargado {alto}x{ancho}.")

        # 3. CALCULAR SI FALLÓ LA CARGA O INCOMPATIBILIDAD
        print("Calculando nuevo fondo...")
        fondo, alto, ancho = self._calcular_fondo_median()

        # Una vez calculado, lo guardamos para la próxima ejecución
        self.image = fondo
        self._guardar_fondo()

        return fondo, alto, ancho

    def _calcular_fondo_median(self):
        if not os.path.exists(self.video_path):
            raise FileNotFoundError(f"No se encuentra el vídeo: {self.video_path}")

        cap = cv2.VideoCapture(self.video_path)
        if not cap.isOpened():
            raise RuntimeError("OpenCV no ha podido abrir el vídeo.")

        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total_frames <= 0:
            cap.release()
            raise ValueError("El vídeo no contiene frames válidos.")

        indices = np.linspace(0, total_frames - 1, self.n_samples, dtype=int)
        frames = []
        alto = ancho = None

        for idx in indices:
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(idx))
            ret, frame = cap.read()
            if not ret:
                continue

            if self.scale != 1.0:
                frame = cv2.resize(frame, (0, 0), fx=self.scale, fy=self.scale)

            if alto is None:
                alto, ancho, _ = frame.shape

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (7, 7), 0)
            frames.append(gray.astype(np.float32))

        cap.release()

        if len(frames) == 0:
            raise RuntimeError("No se han podido leer frames para calcular el fondo.")

        fondo = np.median(np.stack(frames, axis=0), axis=0).astype(np.uint8)
        return fondo, alto, ancho