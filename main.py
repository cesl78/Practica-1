from Background import Background
from Detect_count import VehicleCounter

VIDEO_PATH = "trafico.mp4" # Asegúrate que este nombre es correcto
SCALE = 0.8
DIRECTION = "down"

def main():
    # 1. Generar/Cargar el fondo del vídeo
    # La clase Background ahora se encarga de:
    # a) Intentar cargar "average_background.png".
    # b) Si no existe, calcularlo, guardarlo y luego usarlo.
    bg = Background(VIDEO_PATH, n_samples=60, scale=SCALE)

    # 2. Crear el contador y ejecutarlo
    # Esto sigue igual, ya que la imagen de fondo está en bg.image
    counter = VehicleCounter(
        video_path=VIDEO_PATH,
        background=bg.image,
        height=bg.height,
        width=bg.width,
        scale=SCALE,
        direction=DIRECTION
    )

    counter.run()

if __name__ == "__main__":
    main()