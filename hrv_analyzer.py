"""
HRV Analyzer - Calcula metricas de HRV y nivel de estres
"""
import numpy as np
import neurokit2 as nk
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import base64
from io import BytesIO
from scipy import signal as scipy_signal


class HRVAnalyzer:
    def __init__(self, sampling_rate=500):
        self.sampling_rate = sampling_rate
        self.rr_intervals = None
        self.r_peaks = None
        self.hrv_time = None
        self.hrv_freq = None

    def analyze(self, ecg_signal):
        """
        Analiza la senal ECG y calcula metricas HRV

        Returns:
            dict con metricas, indice de estres e interpretacion
        """
        # 1. Limpiar y procesar la senal ECG
        ecg_cleaned = nk.ecg_clean(ecg_signal, sampling_rate=self.sampling_rate)

        # 2. Detectar picos R
        try:
            r_peaks_info = nk.ecg_peaks(ecg_cleaned, sampling_rate=self.sampling_rate)
            self.r_peaks = r_peaks_info[1]['ECG_R_Peaks']
        except Exception:
            # Metodo alternativo si falla
            self.r_peaks = self._detect_r_peaks_manual(ecg_cleaned)

        if len(self.r_peaks) < 3:
            raise ValueError("No se detectaron suficientes picos R en el ECG")

        # 3. Calcular intervalos R-R (en milisegundos)
        rr_samples = np.diff(self.r_peaks)
        self.rr_intervals = (rr_samples / self.sampling_rate) * 1000  # ms

        # 4. Filtrar intervalos anomalos (artefactos)
        self.rr_intervals = self._filter_rr_intervals(self.rr_intervals)

        if len(self.rr_intervals) < 2:
            raise ValueError("No hay suficientes intervalos R-R validos")

        # 5. Calcular metricas de dominio temporal
        time_metrics = self._calculate_time_domain_metrics()

        # 6. Calcular metricas de dominio frecuencial
        freq_metrics = self._calculate_frequency_domain_metrics()

        # 7. Calcular indice de estres
        stress_info = self._calculate_stress_index(time_metrics, freq_metrics)

        # 8. Generar interpretacion
        interpretation = self._generate_interpretation(time_metrics, freq_metrics, stress_info)

        # 9. Calcular series temporales para graficos de evolucion
        time_series = self._calculate_time_series()

        return {
            'metrics': {
                'time_domain': time_metrics,
                'frequency_domain': freq_metrics
            },
            'stress': stress_info,
            'interpretation': interpretation,
            'time_series': time_series
        }

    def _detect_r_peaks_manual(self, ecg_signal):
        """Deteccion manual de picos R como respaldo"""
        # Encontrar picos prominentes
        distance = int(0.3 * self.sampling_rate)  # Minimo 300ms entre picos
        peaks, _ = scipy_signal.find_peaks(
            ecg_signal,
            distance=distance,
            prominence=0.3 * np.std(ecg_signal)
        )
        return peaks

    def _filter_rr_intervals(self, rr_intervals):
        """Filtra intervalos R-R anomalos"""
        # Rango fisiologico normal: 300-2000 ms (30-200 bpm)
        mask = (rr_intervals > 300) & (rr_intervals < 2000)

        # Filtrar outliers usando IQR
        q1 = np.percentile(rr_intervals, 25)
        q3 = np.percentile(rr_intervals, 75)
        iqr = q3 - q1
        lower_bound = q1 - 1.5 * iqr
        upper_bound = q3 + 1.5 * iqr

        mask = mask & (rr_intervals >= lower_bound) & (rr_intervals <= upper_bound)

        return rr_intervals[mask]

    def _calculate_time_series(self):
        """
        Calcula series temporales para visualizacion de evolucion de metricas.
        Cada serie tiene timestamps (en segundos) y valores.
        """
        rr = self.rr_intervals

        # Crear eje temporal acumulativo (posicion de cada latido)
        time_axis = np.cumsum(rr) / 1000  # Convertir a segundos
        time_axis = time_axis - time_axis[0]  # Empezar en 0

        time_series = {}

        # 1. HR instantaneo (bpm) - valor por cada latido
        hr_instant = 60000 / rr
        time_series['hr'] = {
            'timestamps': time_axis.tolist(),
            'values': hr_instant.tolist(),
            'label': 'Frecuencia Cardiaca',
            'unit': 'bpm',
            'color': '#EF4444'
        }

        # 2. RR instantaneo (ms)
        time_series['rr'] = {
            'timestamps': time_axis.tolist(),
            'values': rr.tolist(),
            'label': 'Intervalo R-R',
            'unit': 'ms',
            'color': '#3B82F6'
        }

        # 3-5. Metricas con ventana deslizante (SDNN, RMSSD, pNN50)
        window_size = max(8, len(rr) // 5)  # Ventana adaptativa (~5s)
        step = max(1, window_size // 3)  # Solapamiento 66%

        sdnn_series = []
        rmssd_series = []
        pnn50_series = []
        window_times = []

        for i in range(0, len(rr) - window_size + 1, step):
            window = rr[i:i + window_size]
            window_time = time_axis[i + window_size // 2]  # Centro de ventana
            window_times.append(float(window_time))

            # SDNN
            sdnn_series.append(float(np.std(window, ddof=1)))

            # RMSSD
            diff_rr = np.diff(window)
            rmssd_series.append(float(np.sqrt(np.mean(diff_rr ** 2))))

            # pNN50
            nn50 = np.sum(np.abs(diff_rr) > 50)
            pnn50_series.append(float((nn50 / len(diff_rr)) * 100))

        time_series['sdnn'] = {
            'timestamps': window_times,
            'values': sdnn_series,
            'label': 'SDNN',
            'unit': 'ms',
            'color': '#10B981'
        }

        time_series['rmssd'] = {
            'timestamps': window_times,
            'values': rmssd_series,
            'label': 'RMSSD',
            'unit': 'ms',
            'color': '#8B5CF6'
        }

        time_series['pnn50'] = {
            'timestamps': window_times,
            'values': pnn50_series,
            'label': 'pNN50',
            'unit': '%',
            'color': '#F59E0B'
        }

        # 6-10. Metricas frecuenciales (segmentos)
        freq_series = self._calculate_frequency_time_series(time_axis)
        time_series.update(freq_series)

        return time_series

    def _calculate_frequency_time_series(self, time_axis):
        """
        Calcula evolucion de metricas frecuenciales usando segmentos.
        """
        rr = self.rr_intervals

        # Necesitamos al menos ~10 segundos por segmento para analisis frecuencial
        total_duration = float(time_axis[-1])
        segment_duration = min(10, total_duration / 3)  # 3 segmentos minimo

        if total_duration < 12:  # Muy corto para segmentar
            return {}

        segment_times = []
        lf_series = []
        hf_series = []
        ratio_series = []
        lf_nu_series = []
        hf_nu_series = []

        # Usar ventanas solapadas
        step = segment_duration / 2
        current_time = 0

        while current_time + segment_duration <= total_duration:
            # Encontrar indices del segmento
            mask = (time_axis >= current_time) & (time_axis < current_time + segment_duration)
            segment_rr = rr[mask]

            if len(segment_rr) >= 8:  # Minimo para analisis
                freq_metrics = self._analyze_segment_frequency(segment_rr)

                segment_times.append(float(current_time + segment_duration / 2))
                lf_series.append(freq_metrics['lf_power'])
                hf_series.append(freq_metrics['hf_power'])
                ratio_series.append(freq_metrics['lf_hf_ratio'])
                lf_nu_series.append(freq_metrics['lf_nu'])
                hf_nu_series.append(freq_metrics['hf_nu'])

            current_time += step

        if len(segment_times) == 0:
            return {}

        return {
            'lf': {
                'timestamps': segment_times,
                'values': lf_series,
                'label': 'LF Power',
                'unit': 'ms²',
                'color': '#EF4444'
            },
            'hf': {
                'timestamps': segment_times,
                'values': hf_series,
                'label': 'HF Power',
                'unit': 'ms²',
                'color': '#10B981'
            },
            'lfhf': {
                'timestamps': segment_times,
                'values': ratio_series,
                'label': 'LF/HF Ratio',
                'unit': '',
                'color': '#F59E0B'
            },
            'lfnu': {
                'timestamps': segment_times,
                'values': lf_nu_series,
                'label': 'LF Normalizado',
                'unit': '%',
                'color': '#EF4444'
            },
            'hfnu': {
                'timestamps': segment_times,
                'values': hf_nu_series,
                'label': 'HF Normalizado',
                'unit': '%',
                'color': '#10B981'
            }
        }

    def _analyze_segment_frequency(self, rr_segment):
        """Analiza metricas frecuenciales de un segmento RR"""
        # Interpolar a senal uniforme
        time_rr = np.cumsum(rr_segment) / 1000
        time_rr = time_rr - time_rr[0]

        fs_interp = 4  # Hz
        time_interp = np.arange(0, time_rr[-1], 1/fs_interp)

        if len(time_interp) < 4:
            return {'lf_power': 0, 'hf_power': 0, 'lf_hf_ratio': 0, 'lf_nu': 0, 'hf_nu': 0}

        rr_interp = np.interp(time_interp, time_rr, rr_segment)
        rr_detrend = scipy_signal.detrend(rr_interp)

        nperseg = min(len(rr_detrend), 64)
        frequencies, psd = scipy_signal.welch(rr_detrend, fs=fs_interp, nperseg=nperseg)

        # Calcular potencia en bandas
        lf_mask = (frequencies >= 0.04) & (frequencies < 0.15)
        hf_mask = (frequencies >= 0.15) & (frequencies < 0.4)

        lf_power = float(np.trapz(psd[lf_mask], frequencies[lf_mask])) if np.any(lf_mask) else 0
        hf_power = float(np.trapz(psd[hf_mask], frequencies[hf_mask])) if np.any(hf_mask) else 0

        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0
        lf_hf_sum = lf_power + hf_power
        lf_nu = (lf_power / lf_hf_sum) * 100 if lf_hf_sum > 0 else 0
        hf_nu = (hf_power / lf_hf_sum) * 100 if lf_hf_sum > 0 else 0

        return {
            'lf_power': round(lf_power, 2),
            'hf_power': round(hf_power, 2),
            'lf_hf_ratio': round(lf_hf_ratio, 2),
            'lf_nu': round(lf_nu, 1),
            'hf_nu': round(hf_nu, 1)
        }

    def _calculate_time_domain_metrics(self):
        """Calcula metricas de HRV en dominio temporal"""
        rr = self.rr_intervals

        # Frecuencia cardiaca media
        hr_mean = 60000 / np.mean(rr)  # bpm

        # SDNN: Desviacion estandar de intervalos NN
        sdnn = np.std(rr, ddof=1)

        # RMSSD: Raiz cuadrada de la media de las diferencias al cuadrado
        diff_rr = np.diff(rr)
        rmssd = np.sqrt(np.mean(diff_rr ** 2))

        # pNN50: Porcentaje de intervalos que difieren mas de 50ms
        nn50 = np.sum(np.abs(diff_rr) > 50)
        pnn50 = (nn50 / len(diff_rr)) * 100 if len(diff_rr) > 0 else 0

        # pNN20: Porcentaje de intervalos que difieren mas de 20ms
        nn20 = np.sum(np.abs(diff_rr) > 20)
        pnn20 = (nn20 / len(diff_rr)) * 100 if len(diff_rr) > 0 else 0

        # RR medio
        rr_mean = np.mean(rr)

        # Rango RR
        rr_range = np.max(rr) - np.min(rr)

        return {
            'hr_mean': round(hr_mean, 1),
            'sdnn': round(sdnn, 2),
            'rmssd': round(rmssd, 2),
            'pnn50': round(pnn50, 2),
            'pnn20': round(pnn20, 2),
            'rr_mean': round(rr_mean, 2),
            'rr_range': round(rr_range, 2),
            'total_beats': len(self.r_peaks)
        }

    def _calculate_frequency_domain_metrics(self):
        """Calcula metricas de HRV en dominio frecuencial"""
        rr = self.rr_intervals

        if len(rr) < 10:
            return {
                'lf_power': 0,
                'hf_power': 0,
                'lf_hf_ratio': 0,
                'total_power': 0,
                'vlf_power': 0,
                'lf_nu': 0,
                'hf_nu': 0
            }

        # Interpolar RR a una senal uniformemente muestreada
        # Crear eje de tiempo acumulativo
        time_rr = np.cumsum(rr) / 1000  # en segundos
        time_rr = time_rr - time_rr[0]  # empezar en 0

        # Interpolar a 4 Hz (suficiente para analisis de HRV)
        fs_interp = 4  # Hz
        time_interp = np.arange(0, time_rr[-1], 1/fs_interp)

        if len(time_interp) < 4:
            return {
                'lf_power': 0,
                'hf_power': 0,
                'lf_hf_ratio': 0,
                'total_power': 0,
                'vlf_power': 0,
                'lf_nu': 0,
                'hf_nu': 0
            }

        rr_interp = np.interp(time_interp, time_rr, rr)

        # Remover tendencia
        rr_detrend = scipy_signal.detrend(rr_interp)

        # Calcular PSD usando metodo de Welch
        nperseg = min(len(rr_detrend), 256)
        frequencies, psd = scipy_signal.welch(
            rr_detrend,
            fs=fs_interp,
            nperseg=nperseg,
            noverlap=nperseg//2
        )

        # Guardar para grafico
        self.frequencies = frequencies
        self.psd = psd

        # Bandas de frecuencia
        vlf_band = (0.003, 0.04)  # Very Low Frequency
        lf_band = (0.04, 0.15)    # Low Frequency
        hf_band = (0.15, 0.4)     # High Frequency

        # Calcular potencia en cada banda
        vlf_mask = (frequencies >= vlf_band[0]) & (frequencies < vlf_band[1])
        lf_mask = (frequencies >= lf_band[0]) & (frequencies < lf_band[1])
        hf_mask = (frequencies >= hf_band[0]) & (frequencies < hf_band[1])

        vlf_power = np.trapz(psd[vlf_mask], frequencies[vlf_mask]) if np.any(vlf_mask) else 0
        lf_power = np.trapz(psd[lf_mask], frequencies[lf_mask]) if np.any(lf_mask) else 0
        hf_power = np.trapz(psd[hf_mask], frequencies[hf_mask]) if np.any(hf_mask) else 0

        total_power = vlf_power + lf_power + hf_power

        # LF/HF ratio
        lf_hf_ratio = lf_power / hf_power if hf_power > 0 else 0

        # Unidades normalizadas
        lf_hf_sum = lf_power + hf_power
        lf_nu = (lf_power / lf_hf_sum) * 100 if lf_hf_sum > 0 else 0
        hf_nu = (hf_power / lf_hf_sum) * 100 if lf_hf_sum > 0 else 0

        return {
            'vlf_power': round(vlf_power, 2),
            'lf_power': round(lf_power, 2),
            'hf_power': round(hf_power, 2),
            'total_power': round(total_power, 2),
            'lf_hf_ratio': round(lf_hf_ratio, 2),
            'lf_nu': round(lf_nu, 1),
            'hf_nu': round(hf_nu, 1)
        }

    def _calculate_stress_index(self, time_metrics, freq_metrics):
        """
        Calcula el indice de estres basado en metricas HRV

        El estres se asocia con:
        - RMSSD bajo (menor actividad parasimpatica)
        - LF/HF alto (mayor activacion simpatica)
        - HR alto
        """
        # Normalizar metricas a escala 0-100

        # RMSSD: valores tipicos 20-100ms, menor = mas estres
        rmssd = time_metrics['rmssd']
        rmssd_score = max(0, min(100, (100 - rmssd) * 1.5))

        # LF/HF ratio: valores tipicos 0.5-3, mayor = mas estres
        lf_hf = freq_metrics['lf_hf_ratio']
        lf_hf_score = max(0, min(100, lf_hf * 25))

        # HR: valores tipicos 50-100, mayor = mas estres
        hr = time_metrics['hr_mean']
        hr_score = max(0, min(100, (hr - 50) * 2))

        # SDNN bajo = mas estres
        sdnn = time_metrics['sdnn']
        sdnn_score = max(0, min(100, (100 - sdnn) * 1.2))

        # Calcular indice combinado de estres
        stress_score = (
            rmssd_score * 0.35 +
            lf_hf_score * 0.25 +
            hr_score * 0.20 +
            sdnn_score * 0.20
        )

        # Determinar nivel
        if stress_score < 30:
            level = 'bajo'
            color = 'green'
            description = 'Estas relajado/a'
        elif stress_score < 50:
            level = 'normal'
            color = 'blue'
            description = 'Nivel de estres normal'
        elif stress_score < 70:
            level = 'moderado'
            color = 'orange'
            description = 'Estres moderado detectado'
        else:
            level = 'alto'
            color = 'red'
            description = 'Nivel de estres elevado'

        return {
            'score': round(stress_score, 1),
            'level': level,
            'color': color,
            'description': description,
            'components': {
                'rmssd_contribution': round(rmssd_score * 0.35, 1),
                'lf_hf_contribution': round(lf_hf_score * 0.25, 1),
                'hr_contribution': round(hr_score * 0.20, 1),
                'sdnn_contribution': round(sdnn_score * 0.20, 1)
            }
        }

    def _generate_interpretation(self, time_metrics, freq_metrics, stress_info):
        """Genera una interpretacion textual de los resultados"""
        interpretations = []

        # Interpretar frecuencia cardiaca
        hr = time_metrics['hr_mean']
        if hr < 60:
            interpretations.append(f"Tu frecuencia cardiaca ({hr} bpm) es bradicardica (baja), lo cual puede indicar buena forma fisica.")
        elif hr > 100:
            interpretations.append(f"Tu frecuencia cardiaca ({hr} bpm) es taquicardica (alta). Considera relajarte.")
        else:
            interpretations.append(f"Tu frecuencia cardiaca ({hr} bpm) esta en rango normal.")

        # Interpretar RMSSD
        rmssd = time_metrics['rmssd']
        if rmssd > 50:
            interpretations.append(f"Tu RMSSD ({rmssd} ms) indica buena actividad parasimpatica y capacidad de recuperacion.")
        elif rmssd > 20:
            interpretations.append(f"Tu RMSSD ({rmssd} ms) esta en rango normal.")
        else:
            interpretations.append(f"Tu RMSSD ({rmssd} ms) es bajo, indicando posible fatiga o estres.")

        # Interpretar SDNN
        sdnn = time_metrics['sdnn']
        if sdnn > 100:
            interpretations.append(f"Tu SDNN ({sdnn} ms) indica excelente variabilidad cardiaca general.")
        elif sdnn > 50:
            interpretations.append(f"Tu SDNN ({sdnn} ms) indica variabilidad cardiaca saludable.")
        else:
            interpretations.append(f"Tu SDNN ({sdnn} ms) sugiere variabilidad reducida.")

        # Interpretar balance simpatico/parasimpatico
        lf_hf = freq_metrics['lf_hf_ratio']
        if lf_hf < 1:
            interpretations.append(f"El ratio LF/HF ({lf_hf}) indica predominancia parasimpatica (relajacion).")
        elif lf_hf < 2:
            interpretations.append(f"El ratio LF/HF ({lf_hf}) indica buen balance autonomico.")
        else:
            interpretations.append(f"El ratio LF/HF ({lf_hf}) indica predominancia simpatica (activacion/estres).")

        # Resumen de estres
        interpretations.append(f"\n**Nivel de Estres: {stress_info['level'].upper()}** (puntuacion: {stress_info['score']}/100)")
        interpretations.append(stress_info['description'])

        return interpretations

    def generate_poincare_plot(self):
        """Genera grafico de Poincare (RRn vs RRn+1)"""
        if self.rr_intervals is None or len(self.rr_intervals) < 2:
            return None

        rr = self.rr_intervals

        fig, ax = plt.subplots(figsize=(6, 6))

        # Plot RRn vs RRn+1
        ax.scatter(rr[:-1], rr[1:], alpha=0.6, c='#FF6B35', s=30)

        # Linea de identidad
        min_rr = min(rr)
        max_rr = max(rr)
        ax.plot([min_rr, max_rr], [min_rr, max_rr], 'k--', alpha=0.3)

        # Calcular SD1 y SD2 para la elipse
        sd1, sd2 = self._calculate_poincare_indices()

        # Dibujar elipse
        from matplotlib.patches import Ellipse
        mean_rr = np.mean(rr)
        ellipse = Ellipse(
            (mean_rr, mean_rr),
            width=sd2*2,
            height=sd1*2,
            angle=45,
            fill=False,
            color='blue',
            linewidth=2
        )
        ax.add_patch(ellipse)

        ax.set_xlabel('RR(n) [ms]')
        ax.set_ylabel('RR(n+1) [ms]')
        ax.set_title(f'Grafico de Poincare\nSD1={sd1:.1f}ms, SD2={sd2:.1f}ms')
        ax.grid(True, alpha=0.3)
        ax.set_aspect('equal')

        # Convertir a base64
        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

        return image_base64

    def _calculate_poincare_indices(self):
        """Calcula indices SD1 y SD2 de Poincare"""
        rr = self.rr_intervals
        diff_rr = np.diff(rr)

        # SD1: variabilidad a corto plazo
        sd1 = np.std(diff_rr) / np.sqrt(2)

        # SD2: variabilidad a largo plazo
        sum_rr = rr[:-1] + rr[1:]
        sd2 = np.sqrt(2 * np.var(rr) - 0.5 * np.var(diff_rr))

        return sd1, sd2

    def generate_rr_histogram(self):
        """Genera histograma de intervalos R-R"""
        if self.rr_intervals is None or len(self.rr_intervals) < 2:
            return None

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.hist(self.rr_intervals, bins=20, color='#FF6B35', alpha=0.7, edgecolor='white')
        ax.axvline(np.mean(self.rr_intervals), color='blue', linestyle='--',
                   label=f'Media: {np.mean(self.rr_intervals):.0f} ms')
        ax.set_xlabel('Intervalo RR [ms]')
        ax.set_ylabel('Frecuencia')
        ax.set_title('Distribucion de Intervalos R-R')
        ax.legend()
        ax.grid(True, alpha=0.3)

        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

        return image_base64

    def generate_frequency_plot(self):
        """Genera grafico de espectro de frecuencias"""
        if not hasattr(self, 'frequencies') or not hasattr(self, 'psd'):
            return None

        fig, ax = plt.subplots(figsize=(8, 4))

        # Grafico de PSD
        ax.semilogy(self.frequencies, self.psd, 'b-', linewidth=1)

        # Marcar bandas de frecuencia
        ax.axvspan(0.003, 0.04, alpha=0.2, color='gray', label='VLF')
        ax.axvspan(0.04, 0.15, alpha=0.2, color='yellow', label='LF')
        ax.axvspan(0.15, 0.4, alpha=0.2, color='green', label='HF')

        ax.set_xlabel('Frecuencia [Hz]')
        ax.set_ylabel('PSD [ms^2/Hz]')
        ax.set_title('Densidad Espectral de Potencia')
        ax.set_xlim(0, 0.5)
        ax.legend()
        ax.grid(True, alpha=0.3)

        buffer = BytesIO()
        fig.savefig(buffer, format='png', dpi=100, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)

        return image_base64
