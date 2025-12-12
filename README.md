Implementación de un Sistema de Conteo de Vehículos mediante Visión Artificial

Este proyecto implementa un sistema de detección, seguimiento y conteo de vehículos a partir de un vídeo de tráfico con cámara fija, utilizando técnicas clásicas de Visión Artificial.
El objetivo es contabilizar los vehículos que aparecen en una vía de tráfico desde el inicio del vídeo, cumpliendo los requisitos establecidos en la práctica de la asignatura.

El sistema se basa en sustracción de fondo, detección por contornos y tracking manual, evitando el uso de técnicas de aprendizaje automático para garantizar un comportamiento determinista y explicable.

Descripción del Proyecto

El sistema analiza un vídeo de tráfico real capturado por una cámara fija y detecta los vehículos en movimiento respecto a un fondo estático. Cada vehículo detectado se sigue a lo largo de varios frames y se contabiliza aplicando criterios temporales y geométricos que reducen errores habituales como:

Dobles conteos

Conteos por ruido o sombras

Detecciones espurias de corta duración

El proyecto pone especial énfasis en la robustez del conteo, incluso en situaciones donde varios vehículos circulan muy próximos entre sí.

Técnicas Implementadas
1. Sustracción de Fondo

Se calcula un fondo promedio del vídeo utilizando la mediana de múltiples frames muestreados uniformemente a lo largo del tiempo.
Este fondo se utiliza como referencia para detectar objetos en movimiento.

2. Detección por Contornos

A partir de la diferencia entre el frame actual y el fondo:

Conversión a escala de grises

Suavizado Gaussiano

Umbralización binaria

Operaciones morfológicas (apertura y cierre)

Extracción de contornos relevantes

3. Filtrado Geométrico

Las detecciones se restringen a una región válida correspondiente a los carriles de interés, descartando automáticamente zonas irrelevantes de la escena.

Este filtrado se aplica únicamente como criterio interno, sin representarse visualmente, para no interferir en la interpretación de los resultados.

4. Tracking Manual

Cada vehículo detectado se modela mediante una estructura Track, que almacena:

Identificador único

Posición actual

Posición inicial

Número de frames visibles

Estado de conteo

La asociación entre detecciones se realiza usando la distancia euclídea entre centroides en frames consecutivos.

5. Conteo de Vehículos

Un vehículo se contabiliza cuando:

Ha sido visible durante un número mínimo de frames consecutivos

Ha realizado un desplazamiento vertical suficiente

Este criterio evita dobles conteos y detecciones espurias debidas a ruido o sombras.

Estructura del Código

El proyecto sigue una arquitectura modular:

Archivo	Descripción
main.py	Script principal. Inicializa el sistema, calcula el fondo y ejecuta el conteo.
Background.py	Cálculo del fondo promedio mediante muestreo temporal del vídeo.
Detect_count.py	Núcleo del sistema: detección, tracking y conteo de vehículos.
Track.py	Definición de la estructura de seguimiento de cada vehículo.
trafico.mp4	Vídeo de entrada utilizado para el análisis.
Flujo de Ejecución

Se calcula (o carga) el fondo del vídeo.

Se procesa cada frame:

Detección de movimiento

Extracción de contornos

Filtrado geométrico

Se asocian detecciones a tracks existentes.

Se crean nuevos tracks cuando aparece un vehículo.

Se contabilizan los vehículos cuando cumplen los criterios establecidos.

Se muestran los resultados en tiempo real.

Resultados

El sistema proporciona un conteo estable y coherente con el análisis manual del vídeo, con un margen de error máximo de ±1 vehículo, considerado aceptable dadas las limitaciones del enfoque clásico utilizado.

Durante el desarrollo se evaluaron distintas estrategias (líneas virtuales, regiones múltiples, separación por sentido), seleccionándose finalmente la solución más robusta para la escena concreta analizada.

Instalación y Uso
Requisitos

Python 3.8 o superior

Librerías:

opencv-python

numpy

Ejecución

Colocar todos los archivos en el mismo directorio y ejecutar:

python main.py


Durante la ejecución se mostrarán:

La máscara binaria de detección

El vídeo con las detecciones y el conteo actualizado

Limitaciones

El sistema está diseñado para cámaras fijas

Cambios bruscos de iluminación pueden afectar a la sustracción de fondo

No se diferencian tipos de vehículos

Oclusiones prolongadas pueden afectar al tracking

Estas limitaciones son inherentes a las técnicas clásicas empleadas.

Conclusión

Este proyecto implementa un sistema completo de detección, seguimiento y conteo de vehículos utilizando técnicas de visión artificial explicables y eficientes. La solución cumple los requisitos del enunciado y demuestra un uso correcto de OpenCV y estructuras de datos orientadas a la robustez del sistema.
