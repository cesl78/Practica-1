import numpy as np

class Track:
    """
    Representa un vehículo detectado y seguido entre frames consecutivos.
    """
    def __init__(self, track_id, cx, cy):
        self.id = track_id
        self.cx = cx
        self.cy = cy
        self.last_cy = cy          # posición anterior (por si se quiere usar)
        self.start_cy = cy         # posición inicial (evitar doble conteo)
        self.counted = False
        self.missed = 0
        self.visible_frames = 1    # frames consecutivos visibles


def distancia(p1, p2):
    return np.linalg.norm(np.array(p1) - np.array(p2))
