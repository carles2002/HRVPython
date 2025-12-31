"""
ECG Processor - Extrae senal ECG de imagenes/PDFs
"""
import numpy as np
import cv2
from PIL import Image
import fitz  # PyMuPDF
import base64
from io import BytesIO
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.ndimage import gaussian_filter1d
from scipy.interpolate import interp1d


class ECGProcessor:
    def __init__(self):
        # Color naranja de Samsung Health Monitor (aproximado)
        self.orange_lower = np.array([5, 100, 100])   # HSV lower bound
        self.orange_upper = np.array([25, 255, 255])  # HSV upper bound
        # Frecuencia de muestreo objetivo
        self.target_sampling_rate = 500  # Hz

    def process_file(self, filepath):
        """
        Procesa un archivo PDF o imagen y extrae la senal ECG

        Returns:
            ecg_signal: numpy array con la senal ECG
            sampling_rate: frecuencia de muestreo
            ecg_plot_base64: grafico del ECG en base64
        """
        # Determinar tipo de archivo
        if filepath.lower().endswith('.pdf'):
            image = self._extract_image_from_pdf(filepath)
        else:
            image = cv2.imread(filepath)
            if image is None:
                raise ValueError(f"No se pudo leer la imagen: {filepath}")

        # Extraer senal ECG de la imagen
        ecg_signal = self._extract_ecg_signal(image)

        # Generar grafico del ECG
        ecg_plot_base64 = self._generate_ecg_plot(ecg_signal)

        return ecg_signal, self.target_sampling_rate, ecg_plot_base64

    def _extract_image_from_pdf(self, pdf_path):
        """Extrae la imagen del PDF renderizandolo a alta resolucion"""
        doc = fitz.open(pdf_path)
        page = doc[0]  # Primera pagina

        # Renderizar a alta resolucion (300 DPI)
        mat = fitz.Matrix(3, 3)  # Escala 3x
        pix = page.get_pixmap(matrix=mat)

        # Convertir a numpy array
        img_data = pix.tobytes("png")
        nparr = np.frombuffer(img_data, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        doc.close()
        return image

    def _extract_ecg_signal(self, image):
        """
        Extrae la senal ECG de la imagen detectando la linea naranja

        El grafico de Samsung Health tiene 3 filas de 10 segundos cada una
        """
        # Convertir a HSV para detectar color naranja
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # Crear mascara para el color naranja
        mask = cv2.inRange(hsv, self.orange_lower, self.orange_upper)

        # Tambien detectar lineas rojas/naranjas en caso de otros formatos
        # Ampliar rango para capturar mas tonos
        orange_lower2 = np.array([0, 80, 80])
        orange_upper2 = np.array([30, 255, 255])
        mask2 = cv2.inRange(hsv, orange_lower2, orange_upper2)
        mask = cv2.bitwise_or(mask, mask2)

        # Aplicar operaciones morfologicas para limpiar la mascara
        kernel = np.ones((3, 3), np.uint8)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)

        # Detectar las 3 filas del grafico ECG
        rows = self._detect_ecg_rows(mask, image.shape)

        if not rows:
            # Si no se detectan filas, intentar con toda la imagen
            rows = [(0, image.shape[0])]

        # Extraer senal de cada fila y concatenar
        all_signals = []
        for row_start, row_end in rows:
            row_mask = mask[row_start:row_end, :]
            row_signal = self._extract_signal_from_row(row_mask)
            if len(row_signal) > 0:
                all_signals.append(row_signal)

        if not all_signals:
            raise ValueError("No se pudo extraer la senal ECG de la imagen")

        # Concatenar todas las senales
        ecg_signal = np.concatenate(all_signals)

        # Normalizar la senal
        ecg_signal = self._normalize_signal(ecg_signal)

        # Interpolar a frecuencia de muestreo constante
        # Asumiendo 30 segundos de grabacion total
        duration = 30  # segundos
        ecg_signal = self._resample_signal(ecg_signal, duration)

        return ecg_signal

    def _detect_ecg_rows(self, mask, image_shape):
        """Detecta las filas del grafico ECG"""
        height = image_shape[0]

        # Calcular proyeccion horizontal (suma de pixeles por fila)
        h_projection = np.sum(mask, axis=1)

        # Suavizar la proyeccion
        h_projection = gaussian_filter1d(h_projection.astype(float), sigma=10)

        # Encontrar regiones con actividad (picos en la proyeccion)
        threshold = np.max(h_projection) * 0.1

        # Buscar regiones continuas por encima del umbral
        active = h_projection > threshold
        rows = []
        start = None

        for i in range(len(active)):
            if active[i] and start is None:
                start = i
            elif not active[i] and start is not None:
                if i - start > height * 0.05:  # Region minima
                    rows.append((start, i))
                start = None

        if start is not None:
            rows.append((start, len(active)))

        # Si se detectan exactamente 3 filas, perfecto
        # Si no, intentar dividir la imagen en 3 partes iguales
        if len(rows) < 3:
            # Buscar el area principal del grafico (excluyendo cabecera/pie)
            if rows:
                min_y = min(r[0] for r in rows)
                max_y = max(r[1] for r in rows)
            else:
                min_y = int(height * 0.15)  # Excluir cabecera
                max_y = int(height * 0.85)  # Excluir pie

            # Dividir en 3 filas
            row_height = (max_y - min_y) // 3
            rows = [
                (min_y, min_y + row_height),
                (min_y + row_height, min_y + 2 * row_height),
                (min_y + 2 * row_height, max_y)
            ]

        return rows[:3]  # Maximo 3 filas

    def _extract_signal_from_row(self, row_mask):
        """Extrae la senal de una fila del grafico"""
        width = row_mask.shape[1]
        signal = []

        for x in range(width):
            column = row_mask[:, x]
            # Encontrar pixeles activos en esta columna
            active_pixels = np.where(column > 0)[0]

            if len(active_pixels) > 0:
                # Usar el centroide de los pixeles activos como valor Y
                y_value = np.mean(active_pixels)
                signal.append(y_value)
            elif signal:  # Si ya tenemos datos, interpolar
                signal.append(signal[-1])

        return np.array(signal)

    def _normalize_signal(self, signal):
        """Normaliza la senal ECG"""
        if len(signal) == 0:
            return signal

        # Invertir (en imagen Y crece hacia abajo)
        signal = -signal

        # Centrar en cero
        signal = signal - np.mean(signal)

        # Normalizar a rango [-1, 1]
        max_val = np.max(np.abs(signal))
        if max_val > 0:
            signal = signal / max_val

        # Aplicar filtro suave para eliminar ruido
        signal = gaussian_filter1d(signal, sigma=2)

        return signal

    def _resample_signal(self, signal, duration):
        """Resamplea la senal a la frecuencia objetivo"""
        num_samples = int(duration * self.target_sampling_rate)
        x_original = np.linspace(0, duration, len(signal))
        x_new = np.linspace(0, duration, num_samples)

        # Interpolar
        f = interp1d(x_original, signal, kind='cubic', fill_value='extrapolate')
        resampled = f(x_new)

        return resampled

    def _generate_ecg_plot(self, ecg_signal):
        """Genera un grafico del ECG procesado y lo devuelve en base64"""
        fig, ax = plt.subplots(figsize=(12, 4))

        # Crear eje de tiempo
        duration = len(ecg_signal) / self.target_sampling_rate
        time = np.linspace(0, duration, len(ecg_signal))

        ax.plot(time, ecg_signal, 'r-', linewidth=0.8)
        ax.set_xlabel('Tiempo (s)')
        ax.set_ylabel('Amplitud')
        ax.set_title('Senal ECG Procesada')
        ax.grid(True, alpha=0.3)
        ax.set_xlim(0, duration)

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

        return image_base64
