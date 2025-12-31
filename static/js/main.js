/**
 * HRV Analyzer - Frontend JavaScript v2.0
 * Con modales informativos, animaciones y visualizaciones mejoradas
 */

// Base de datos de informacion de metricas
const metricInfo = {
    // Dominio Temporal
    hr: {
        icon: '❤️',
        title: 'Frecuencia Cardiaca',
        description: 'La frecuencia cardiaca (FC) es el numero de latidos del corazon por minuto. Es un indicador basico de la actividad cardiovascular.',
        ranges: [
            { range: '< 60 bpm', status: 'good', label: 'Bradicardia', description: 'Puede indicar buena forma fisica o condicion medica' },
            { range: '60-100 bpm', status: 'normal', label: 'Normal', description: 'Rango saludable en reposo' },
            { range: '> 100 bpm', status: 'warning', label: 'Taquicardia', description: 'Puede indicar estres, ejercicio o condicion medica' }
        ],
        tip: 'Una FC en reposo mas baja generalmente indica mejor condicion cardiovascular.'
    },
    sdnn: {
        icon: '📊',
        title: 'SDNN (Desviacion Estandar)',
        description: 'SDNN es la desviacion estandar de todos los intervalos entre latidos (NN). Representa la variabilidad TOTAL del ritmo cardiaco y refleja la salud general del sistema nervioso autonomo.',
        ranges: [
            { range: '> 100 ms', status: 'good', label: 'Excelente', description: 'Alta variabilidad, sistema muy saludable' },
            { range: '50-100 ms', status: 'normal', label: 'Normal', description: 'Variabilidad adecuada' },
            { range: '< 50 ms', status: 'warning', label: 'Bajo', description: 'Variabilidad reducida, posible estres cronico' }
        ],
        tip: 'Valores mas altos de SDNN indican mejor capacidad de adaptacion del corazon.'
    },
    rmssd: {
        icon: '💓',
        title: 'RMSSD',
        description: 'RMSSD (Root Mean Square of Successive Differences) mide la variabilidad a CORTO PLAZO entre latidos consecutivos. Es el mejor indicador de la actividad del sistema nervioso parasimpatico (relajacion).',
        ranges: [
            { range: '> 50 ms', status: 'good', label: 'Excelente', description: 'Fuerte actividad parasimpatica, buena recuperacion' },
            { range: '20-50 ms', status: 'normal', label: 'Normal', description: 'Actividad parasimpatica adecuada' },
            { range: '< 20 ms', status: 'danger', label: 'Bajo', description: 'Actividad parasimpatica reducida, posible estres agudo' }
        ],
        tip: 'RMSSD alto = mejor capacidad de relajacion y recuperacion.'
    },
    pnn50: {
        icon: '📈',
        title: 'pNN50',
        description: 'pNN50 es el porcentaje de intervalos RR consecutivos que difieren mas de 50 milisegundos. Indica cuantos latidos tienen una diferencia significativa con el anterior.',
        ranges: [
            { range: '> 20%', status: 'good', label: 'Excelente', description: 'Alta variabilidad latido a latido' },
            { range: '5-20%', status: 'normal', label: 'Normal', description: 'Variabilidad adecuada' },
            { range: '< 5%', status: 'warning', label: 'Bajo', description: 'Poca variabilidad, ritmo muy regular' }
        ],
        tip: 'Un pNN50 alto indica que tu corazon responde bien a los cambios.'
    },
    rr: {
        icon: '⏱️',
        title: 'Intervalo RR Medio',
        description: 'El intervalo RR es el tiempo promedio entre dos latidos consecutivos, medido en milisegundos. Es la inversa de la frecuencia cardiaca.',
        ranges: [
            { range: '> 1000 ms', status: 'good', label: 'Lento', description: 'Corresponde a < 60 bpm' },
            { range: '600-1000 ms', status: 'normal', label: 'Normal', description: 'Corresponde a 60-100 bpm' },
            { range: '< 600 ms', status: 'warning', label: 'Rapido', description: 'Corresponde a > 100 bpm' }
        ],
        tip: 'RR medio de 750ms = 80 bpm aproximadamente.'
    },

    // Dominio Frecuencial
    lf: {
        icon: '🔥',
        title: 'LF Power (Baja Frecuencia)',
        description: 'LF (Low Frequency) representa la potencia en el rango 0.04-0.15 Hz. Refleja principalmente la actividad del sistema nervioso SIMPATICO (activacion, estres) aunque tambien incluye algo de actividad parasimpatica.',
        ranges: [
            { range: 'Alto', status: 'warning', label: 'Dominancia simpatica', description: 'Mayor activacion/estres' },
            { range: 'Equilibrado', status: 'normal', label: 'Balance', description: 'Equilibrio autonomico' },
            { range: 'Bajo', status: 'good', label: 'Dominancia parasimpatica', description: 'Mayor relajacion' }
        ],
        tip: 'LF elevado puede indicar estres o estado de alerta.'
    },
    hf: {
        icon: '🍃',
        title: 'HF Power (Alta Frecuencia)',
        description: 'HF (High Frequency) representa la potencia en el rango 0.15-0.4 Hz. Refleja EXCLUSIVAMENTE la actividad del sistema nervioso PARASIMPATICO (relajacion, descanso). Esta relacionado con la respiracion.',
        ranges: [
            { range: 'Alto', status: 'good', label: 'Alta actividad parasimpatica', description: 'Buen estado de relajacion' },
            { range: 'Medio', status: 'normal', label: 'Actividad normal', description: 'Balance adecuado' },
            { range: 'Bajo', status: 'warning', label: 'Baja actividad parasimpatica', description: 'Posible estres o fatiga' }
        ],
        tip: 'HF alto = tu cuerpo esta en modo de recuperacion y relajacion.'
    },
    lfhf: {
        icon: '⚖️',
        title: 'Ratio LF/HF',
        description: 'El ratio LF/HF representa el BALANCE entre el sistema nervioso simpatico (activacion) y parasimpatico (relajacion). Es uno de los indicadores mas importantes de estres.',
        ranges: [
            { range: '< 1.0', status: 'good', label: 'Dominancia parasimpatica', description: 'Estado de relajacion' },
            { range: '1.0-2.0', status: 'normal', label: 'Equilibrio', description: 'Balance autonomico saludable' },
            { range: '> 2.0', status: 'warning', label: 'Dominancia simpatica', description: 'Estado de activacion/estres' }
        ],
        tip: 'LF/HF < 1 = relajado | LF/HF > 2 = estresado'
    },
    lfnu: {
        icon: '🔴',
        title: 'LF Normalizado',
        description: 'LF en unidades normalizadas representa el porcentaje de la potencia LF respecto al total (LF+HF). Facilita la comparacion entre mediciones.',
        ranges: [
            { range: '< 40%', status: 'good', label: 'Bajo', description: 'Predomina la relajacion' },
            { range: '40-60%', status: 'normal', label: 'Normal', description: 'Balance adecuado' },
            { range: '> 60%', status: 'warning', label: 'Alto', description: 'Predomina la activacion' }
        ],
        tip: 'LF% + HF% = 100%. Si LF% es alto, HF% es bajo.'
    },
    hfnu: {
        icon: '🟢',
        title: 'HF Normalizado',
        description: 'HF en unidades normalizadas representa el porcentaje de la potencia HF respecto al total (LF+HF). Indica cuanta de tu variabilidad proviene del sistema parasimpatico.',
        ranges: [
            { range: '> 60%', status: 'good', label: 'Alto', description: 'Fuerte actividad parasimpatica' },
            { range: '40-60%', status: 'normal', label: 'Normal', description: 'Balance adecuado' },
            { range: '< 40%', status: 'warning', label: 'Bajo', description: 'Actividad parasimpatica reducida' }
        ],
        tip: 'HF% alto = tu sistema de relajacion esta dominando.'
    },

    // Estres
    stress: {
        icon: '🧠',
        title: 'Indice de Estres',
        description: 'El indice de estres es una puntuacion de 0-100 calculada a partir de multiples metricas HRV. Combina RMSSD, SDNN, LF/HF ratio y frecuencia cardiaca para darte una vision global de tu estado.',
        ranges: [
            { range: '0-30', status: 'good', label: 'Relajado', description: 'Tu sistema nervioso esta en calma' },
            { range: '30-50', status: 'normal', label: 'Normal', description: 'Estado de equilibrio' },
            { range: '50-70', status: 'warning', label: 'Moderado', description: 'Algo de tension detectada' },
            { range: '70-100', status: 'danger', label: 'Alto', description: 'Nivel de estres elevado' }
        ],
        tip: 'Para reducir el estres: respiracion profunda, meditacion, ejercicio moderado, buen sueno.'
    },

    // Graficos
    ecg: {
        icon: '💗',
        title: 'Grafico ECG',
        description: 'El electrocardiograma (ECG) muestra la actividad electrica del corazon a lo largo del tiempo. Cada pico (onda R) representa un latido cardiaco.',
        interpretation: [
            'Los picos altos son las ondas R (latidos)',
            'La distancia entre picos es el intervalo RR',
            'Picos regulares = ritmo estable',
            'Variacion en las distancias = variabilidad (saludable)'
        ],
        tip: 'Un ECG con variacion natural entre latidos indica un corazon saludable.'
    },
    poincare: {
        icon: '🎯',
        title: 'Grafico de Poincare',
        description: 'El grafico de Poincare muestra cada intervalo RR vs el siguiente. Cada punto representa la relacion entre dos latidos consecutivos.',
        interpretation: [
            'SD1 (eje corto): variabilidad a corto plazo',
            'SD2 (eje largo): variabilidad a largo plazo',
            'Nube alargada = buena variabilidad',
            'Nube compacta/redonda = baja variabilidad'
        ],
        tip: 'Una elipse alargada indica un sistema nervioso autonomo saludable.'
    },
    histogram: {
        icon: '📊',
        title: 'Histograma RR',
        description: 'El histograma muestra la distribucion de los intervalos RR. Te indica cuantos latidos tienen cada duracion.',
        interpretation: [
            'Pico estrecho = ritmo muy regular (menos variabilidad)',
            'Pico ancho = mayor variabilidad (mas saludable)',
            'La linea azul marca la media',
            'Forma de campana = distribucion normal'
        ],
        tip: 'Un histograma ancho y suave indica buena variabilidad cardiaca.'
    },
    spectrum: {
        icon: '🌈',
        title: 'Espectro de Frecuencias',
        description: 'El espectro muestra como se distribuye la variabilidad en diferentes frecuencias. Cada banda representa un sistema fisiologico diferente.',
        interpretation: [
            'VLF (gris): procesos muy lentos (termorregulacion)',
            'LF (amarillo): sistema simpatico (activacion)',
            'HF (verde): sistema parasimpatico (relajacion)',
            'Mas area verde = mas relajado'
        ],
        tip: 'Si el area verde (HF) es mayor que la amarilla (LF), estas relajado.'
    }
};

// Emojis de estres segun nivel
const stressEmojis = {
    bajo: '😌',
    normal: '🙂',
    moderado: '😐',
    alto: '😰'
};

// Inicializacion
document.addEventListener('DOMContentLoaded', () => {
    // Elementos del DOM
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const uploadSection = document.getElementById('upload-section');
    const loadingSection = document.getElementById('loading-section');
    const resultsSection = document.getElementById('results-section');
    const errorSection = document.getElementById('error-section');
    const errorMessage = document.getElementById('error-message');
    const newAnalysisBtn = document.getElementById('new-analysis-btn');
    const retryBtn = document.getElementById('retry-btn');
    const modal = document.getElementById('info-modal');
    const modalOverlay = modal.querySelector('.modal-overlay');
    const modalClose = modal.querySelector('.modal-close');

    // Event Listeners para drag and drop
    dropZone.addEventListener('click', () => fileInput.click());

    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('dragover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('dragover');
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFile(e.target.files[0]);
        }
    });

    // Botones
    newAnalysisBtn.addEventListener('click', resetUI);
    retryBtn.addEventListener('click', resetUI);

    // Event listeners para botones de info
    document.querySelectorAll('.info-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.stopPropagation();
            const metricId = btn.getAttribute('data-metric');
            openModal(metricId);
        });
    });

    // Cerrar modal
    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closeModal();
    });

    // Pasos del proceso con porcentajes
    const progressSteps = [
        { percent: 10, text: 'Cargando archivo...' },
        { percent: 25, text: 'Extrayendo imagen del ECG...' },
        { percent: 40, text: 'Procesando senal ECG...' },
        { percent: 55, text: 'Detectando picos R...' },
        { percent: 70, text: 'Calculando metricas HRV...' },
        { percent: 85, text: 'Analizando dominios de frecuencia...' },
        { percent: 95, text: 'Generando visualizaciones...' }
    ];

    let progressInterval = null;
    let currentStepIndex = 0;

    /**
     * Procesa el archivo seleccionado
     */
    function handleFile(file) {
        const extension = file.name.split('.').pop().toLowerCase();
        const validExtensions = ['pdf', 'png', 'jpg', 'jpeg'];

        if (!validExtensions.includes(extension)) {
            showError('Tipo de archivo no valido. Por favor, sube un PDF, PNG o JPG.');
            return;
        }

        showLoading();
        startProgressSimulation();

        const formData = new FormData();
        formData.append('file', file);

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            stopProgressSimulation();
            completeProgress(() => {
                if (data.error) {
                    showError(data.error);
                } else {
                    showResults(data);
                }
            });
        })
        .catch(error => {
            stopProgressSimulation();
            console.error('Error:', error);
            showError('Error de conexion. Asegurate de que el servidor esta funcionando.');
        });
    }

    /**
     * Inicia la simulacion de progreso
     */
    function startProgressSimulation() {
        currentStepIndex = 0;
        updateProgress(progressSteps[0].percent, progressSteps[0].text);

        progressInterval = setInterval(() => {
            currentStepIndex++;
            if (currentStepIndex < progressSteps.length) {
                updateProgress(progressSteps[currentStepIndex].percent, progressSteps[currentStepIndex].text);
            } else {
                stopProgressSimulation();
            }
        }, 1200);
    }

    /**
     * Detiene la simulacion de progreso
     */
    function stopProgressSimulation() {
        if (progressInterval) {
            clearInterval(progressInterval);
            progressInterval = null;
        }
    }

    /**
     * Actualiza la barra de progreso y el texto
     */
    function updateProgress(percent, text) {
        const progressBar = document.getElementById('progress-bar');
        const loadingStep = document.getElementById('loading-step');
        const loadingPercent = document.getElementById('loading-percent');

        if (progressBar) progressBar.style.width = percent + '%';
        if (loadingStep) loadingStep.textContent = text;
        if (loadingPercent) loadingPercent.textContent = percent + '%';
    }

    /**
     * Completa el progreso al 100% y ejecuta callback
     */
    function completeProgress(callback) {
        updateProgress(100, 'Completado!');
        setTimeout(callback, 400);
    }

    /**
     * Muestra la seccion de carga
     */
    function showLoading() {
        uploadSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        loadingSection.classList.remove('hidden');
        updateProgress(0, 'Iniciando...');
    }

    /**
     * Muestra los resultados del analisis
     */
    function showResults(data) {
        loadingSection.classList.add('hidden');
        resultsSection.classList.remove('hidden');

        // Actualizar indicador de estres con gauge
        updateStressGauge(data.stress);

        // Actualizar metricas temporales con estados
        const timeMetrics = data.metrics.time_domain;
        updateMetric('hr-mean', timeMetrics.hr_mean, 'hr');
        updateMetric('sdnn', timeMetrics.sdnn, 'sdnn');
        updateMetric('rmssd', timeMetrics.rmssd, 'rmssd');
        updateMetric('pnn50', timeMetrics.pnn50, 'pnn50');
        updateMetric('rr-mean', timeMetrics.rr_mean, 'rr');

        // Actualizar animacion del corazon segun bpm
        updateHeartAnimation(timeMetrics.hr_mean);

        // Actualizar metricas frecuenciales
        const freqMetrics = data.metrics.frequency_domain;
        updateMetric('lf-power', freqMetrics.lf_power, 'lf');
        updateMetric('hf-power', freqMetrics.hf_power, 'hf');
        updateMetric('lf-hf-ratio', freqMetrics.lf_hf_ratio, 'lfhf');
        document.getElementById('lf-nu').textContent = freqMetrics.lf_nu;
        document.getElementById('hf-nu').textContent = freqMetrics.hf_nu;

        // Actualizar interpretacion
        const interpretationDiv = document.getElementById('interpretation');
        interpretationDiv.innerHTML = data.interpretation
            .map(text => `<p>${formatText(text)}</p>`)
            .join('');

        // Actualizar graficos
        if (data.plots.ecg) {
            document.getElementById('ecg-plot').src = 'data:image/png;base64,' + data.plots.ecg;
        }
        if (data.plots.poincare) {
            document.getElementById('poincare-plot').src = 'data:image/png;base64,' + data.plots.poincare;
        }
        if (data.plots.histogram) {
            document.getElementById('histogram-plot').src = 'data:image/png;base64,' + data.plots.histogram;
        }
        if (data.plots.frequency) {
            document.getElementById('frequency-plot').src = 'data:image/png;base64,' + data.plots.frequency;
        }

        // Scroll suave a resultados
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    /**
     * Actualiza el gauge de estres
     */
    function updateStressGauge(stress) {
        const score = stress.score;
        const level = stress.level;

        // Actualizar texto
        document.getElementById('stress-score').textContent = score;
        document.getElementById('stress-level').textContent = level;
        document.getElementById('stress-level').className = 'stress-level ' + level;
        document.getElementById('stress-description').textContent = stress.description;

        // Actualizar emoji
        document.getElementById('stress-emoji').innerHTML = stressEmojis[level] || '😐';

        // Actualizar gauge SVG
        const gaugeProgress = document.getElementById('gauge-progress');
        const maxDashOffset = 251.2; // Longitud total del arco
        const dashOffset = maxDashOffset - (score / 100) * maxDashOffset;

        // Aplicar clase de color segun nivel
        gaugeProgress.classList.remove('bajo', 'normal', 'moderado', 'alto');
        gaugeProgress.classList.add(level);

        // Animar el gauge
        setTimeout(() => {
            gaugeProgress.style.strokeDashoffset = dashOffset;
        }, 100);
    }

    /**
     * Actualiza una metrica con su estado
     */
    function updateMetric(elementId, value, metricType) {
        const element = document.getElementById(elementId);
        element.textContent = value;

        // Determinar estado y mostrar icono
        const status = getMetricStatus(metricType, value);
        const statusElement = document.getElementById(metricType.replace(/-/g, '') + '-status') ||
                              document.getElementById(elementId.replace(/-mean/, '') + '-status');

        if (statusElement) {
            statusElement.innerHTML = getStatusEmoji(status);
            statusElement.title = status;
        }
    }

    /**
     * Determina el estado de una metrica
     */
    function getMetricStatus(type, value) {
        switch(type) {
            case 'hr':
                if (value < 60) return 'good';
                if (value <= 100) return 'normal';
                return 'warning';
            case 'sdnn':
                if (value > 100) return 'good';
                if (value >= 50) return 'normal';
                return 'warning';
            case 'rmssd':
                if (value > 50) return 'good';
                if (value >= 20) return 'normal';
                return 'danger';
            case 'pnn50':
                if (value > 20) return 'good';
                if (value >= 5) return 'normal';
                return 'warning';
            case 'rr':
                if (value > 1000) return 'good';
                if (value >= 600) return 'normal';
                return 'warning';
            case 'lfhf':
                if (value < 1) return 'good';
                if (value <= 2) return 'normal';
                return 'warning';
            default:
                return 'normal';
        }
    }

    /**
     * Devuelve emoji segun estado
     */
    function getStatusEmoji(status) {
        switch(status) {
            case 'good': return '✅';
            case 'normal': return '🔵';
            case 'warning': return '⚠️';
            case 'danger': return '🔴';
            default: return '';
        }
    }

    /**
     * Actualiza la animacion del corazon segun bpm
     */
    function updateHeartAnimation(bpm) {
        const heartIcon = document.getElementById('hr-icon');
        if (heartIcon) {
            // Calcular duracion de animacion basada en bpm
            // 60 bpm = 1 segundo por latido
            const duration = 60 / bpm;
            heartIcon.style.animationDuration = duration + 's';

            // Cambiar color segun bpm
            if (bpm < 60) {
                heartIcon.style.color = '#10B981'; // Verde
            } else if (bpm <= 100) {
                heartIcon.style.color = '#EF4444'; // Rojo normal
            } else {
                heartIcon.style.color = '#F59E0B'; // Naranja/warning
            }
        }
    }

    /**
     * Abre el modal con informacion de la metrica
     */
    function openModal(metricId) {
        const info = metricInfo[metricId];
        if (!info) return;

        document.getElementById('modal-icon').innerHTML = info.icon;
        document.getElementById('modal-title').textContent = info.title;

        let bodyHTML = `<p>${info.description}</p>`;

        // Rangos de referencia
        if (info.ranges) {
            bodyHTML += '<h4>Rangos de Referencia</h4>';
            info.ranges.forEach(range => {
                bodyHTML += `
                    <div class="range-indicator ${range.status}">
                        <span class="emoji">${getStatusEmoji(range.status)}</span>
                        <div>
                            <strong>${range.range}</strong> - ${range.label}<br>
                            <small>${range.description}</small>
                        </div>
                    </div>
                `;
            });
        }

        // Interpretacion (para graficos)
        if (info.interpretation) {
            bodyHTML += '<h4>Como Interpretarlo</h4><ul>';
            info.interpretation.forEach(item => {
                bodyHTML += `<li>${item}</li>`;
            });
            bodyHTML += '</ul>';
        }

        // Tip
        if (info.tip) {
            bodyHTML += `<h4>💡 Consejo</h4><p><em>${info.tip}</em></p>`;
        }

        document.getElementById('modal-body').innerHTML = bodyHTML;
        modal.classList.add('active');
    }

    /**
     * Cierra el modal
     */
    function closeModal() {
        modal.classList.remove('active');
    }

    /**
     * Muestra un error
     */
    function showError(message) {
        loadingSection.classList.add('hidden');
        uploadSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.remove('hidden');
        errorMessage.textContent = message;
    }

    /**
     * Resetea la interfaz
     */
    function resetUI() {
        uploadSection.classList.remove('hidden');
        loadingSection.classList.add('hidden');
        resultsSection.classList.add('hidden');
        errorSection.classList.add('hidden');
        fileInput.value = '';

        // Reset gauge
        const gaugeProgress = document.getElementById('gauge-progress');
        if (gaugeProgress) {
            gaugeProgress.style.strokeDashoffset = '251.2';
        }

        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    /**
     * Formatea texto con markdown basico
     */
    function formatText(text) {
        return text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }
});
