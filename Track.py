import numpy as np


class Track:
    """
    Representa un vehículo detectado y seguido entre frames consecutivos.
    """
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
    """
    Calcula la distancia euclídea entre dos puntos 2D.
    """
    return np.linalg.norm(np.array(p1) - np.array(p2))
