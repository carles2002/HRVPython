# HRV Analyzer - Analizador de Variabilidad de Frecuencia Cardíaca

Aplicación web local para analizar gráficos ECG (electrocardiograma) y calcular métricas de HRV (Heart Rate Variability) para determinar tu nivel de estrés.

![Version](https://img.shields.io/badge/version-2.0-blue)
![Python](https://img.shields.io/badge/python-3.10+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

---

## 📋 Tabla de Contenidos

- [¿Qué es HRV Analyzer?](#qué-es-hrv-analyzer)
- [Características](#características)
- [Requisitos del Sistema](#requisitos-del-sistema)
- [Instalación](#instalación)
- [Uso](#uso)
- [¿Cómo Funciona?](#cómo-funciona)
- [Métricas Calculadas](#métricas-calculadas)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Troubleshooting](#troubleshooting)

---

## 🎯 ¿Qué es HRV Analyzer?

HRV Analyzer es una aplicación web que procesa archivos PDF o imágenes de electrocardiogramas (como los generados por Samsung Health Monitor) y calcula automáticamente:

- **Variabilidad de frecuencia cardíaca (HRV)**: Medida de cómo varía el tiempo entre latidos
- **Métricas del dominio temporal**: SDNN, RMSSD, pNN50
- **Métricas del dominio frecuencial**: LF Power, HF Power, ratio LF/HF
- **Índice de estrés**: Puntuación de 0-100 indicando tu nivel de estrés actual
- **Visualizaciones avanzadas**: Gráfico de Poincaré, histograma R-R, espectro de frecuencias

---

## ✨ Características

### 🎨 Interfaz Moderna
- **Diseño dark mode** con animaciones suaves
- **Drag & drop** para subir archivos
- **Iconos informativos** con modales explicativos
- **Indicadores de estado** visual para cada métrica (✅⚠️🔴)
- **Gauge circular** animado para visualizar el estrés

### 📊 Análisis Completo
- Detección automática de picos R en el ECG
- Cálculo de intervalos R-R con filtrado de artefactos
- Análisis en dominio temporal y frecuencial
- Generación de 4 gráficos explicativos
- Interpretación personalizada de resultados

### 🧠 Educativo
- Cada métrica tiene un botón de información (ℹ️)
- Modales con explicaciones detalladas
- Rangos de referencia codificados por colores
- Consejos para mejorar tu HRV

### 💓 Animaciones Dinámicas
- Corazón que late según tus bpm
- Velocidad de animación proporcional a tu frecuencia cardíaca
- Colores que cambian según el estado de salud
- Efectos hover y transiciones suaves

---

## 💻 Requisitos del Sistema

### Python
- **Python 3.10 o superior** (Python 3.14 recomendado)

### Librerías Python Necesarias
```
flask >= 3.0.0
neurokit2 >= 0.2.7
numpy >= 1.24.0
opencv-python >= 4.8.0
PyMuPDF >= 1.23.0
matplotlib >= 3.8.0
scipy >= 1.11.0
Pillow >= 10.0.0
```

### Navegador Web
- Chrome, Firefox, Safari o Edge (versiones recientes)
- JavaScript habilitado

---

## 🚀 Instalación

### 1. Clonar o descargar el proyecto

```bash
cd c:\REPO\aitesting\HRV
```

### 2. Instalar las dependencias

**Opción A: Instalación automática (recomendada)**
```bash
pip install -r requirements.txt
```

**Opción B: Instalación manual paso a paso** (si tienes problemas con Python 3.14)

```bash
# Instalar dependencias básicas
pip install flask werkzeug Pillow

# Instalar PyMuPDF
pip install PyMuPDF

# Instalar scipy y matplotlib (solo binarios)
pip install scipy matplotlib --only-binary :all:

# Instalar neurokit2
pip install neurokit2 --only-binary :all:

# Instalar OpenCV
pip install opencv-python --only-binary :all:
```

### 3. Verificar la instalación

```bash
python -c "import flask, neurokit2, cv2, fitz; print('✅ Todas las dependencias instaladas correctamente')"
```

---

## 📱 Uso

### 1. Iniciar el servidor

```bash
python app.py
```

Verás un mensaje como este:
```
==================================================
HRV Analyzer - Servidor iniciado
Abre http://localhost:5000 en tu navegador
==================================================
```

### 2. Abrir en el navegador

Abre tu navegador y ve a:
```
http://localhost:5000
```

### 3. Subir tu archivo ECG

- **Arrastra** el archivo PDF/imagen a la zona de drop, o
- **Haz clic** en la zona para seleccionar el archivo

**Formatos soportados:**
- PDF (como los de Samsung Health Monitor)
- PNG
- JPG/JPEG

### 4. Ver los resultados

La aplicación mostrará:
- **Gauge de estrés**: Indicador circular con tu puntuación 0-100
- **Métricas HRV**: Dominio temporal y frecuencial
- **Interpretación**: Explicación de tus resultados
- **Visualizaciones**: 4 gráficos interactivos

### 5. Explorar información

Haz clic en los **iconos ℹ️** junto a cada métrica para ver:
- Explicación detallada de qué significa
- Rangos de referencia
- Cómo interpretar tu valor
- Consejos para mejorar

---

## 🔬 ¿Cómo Funciona?

### Pipeline de Procesamiento

```
1. ENTRADA
   └─> PDF o Imagen del ECG

2. EXTRACCIÓN DE IMAGEN
   └─> PyMuPDF renderiza el PDF a imagen de alta resolución

3. DETECCIÓN DE LA SEÑAL ECG
   └─> OpenCV detecta los píxeles naranjas (color del ECG de Samsung)
   └─> Convierte la imagen en una señal digital

4. PROCESAMIENTO DE SEÑAL
   └─> NeuroKit2 limpia y filtra la señal
   └─> Detecta los picos R (cada latido)
   └─> Calcula intervalos R-R

5. CÁLCULO DE MÉTRICAS HRV
   └─> Dominio temporal: SDNN, RMSSD, pNN50
   └─> Dominio frecuencial: LF, HF, ratio LF/HF

6. ÍNDICE DE ESTRÉS
   └─> Combina múltiples métricas
   └─> Genera puntuación 0-100

7. VISUALIZACIONES
   └─> Matplotlib genera 4 gráficos
   └─> Convierte a base64 para el navegador

8. SALIDA
   └─> JSON con todas las métricas
   └─> Frontend renderiza los resultados
```

### Algoritmo de Detección ECG

El procesamiento de imagen funciona así:

1. **Conversión a HSV**: La imagen se convierte al espacio de color HSV para detectar mejor el naranja
2. **Creación de máscara**: Se crea una máscara binaria donde solo los píxeles naranjas son blancos
3. **Detección de filas**: El algoritmo detecta las 3 filas del gráfico ECG (10s cada una)
4. **Extracción de señal**: Para cada columna X:
   - Encuentra los píxeles activos en esa columna
   - Calcula el centroide Y (promedio de posiciones)
   - Guarda el punto (X, Y)
5. **Normalización**: Invierte Y, centra en cero, normaliza a [-1, 1]
6. **Remuestreo**: Interpola a 500 Hz de frecuencia constante

### Cálculo del Índice de Estrés

La puntuación de estrés se calcula como:

```
Stress_Score = (rmssd_component * 0.35) +
               (lf_hf_component * 0.25) +
               (hr_component * 0.20) +
               (sdnn_component * 0.20)
```

Donde:
- **RMSSD bajo** = más estrés (35% del peso)
- **LF/HF alto** = más estrés (25% del peso)
- **HR alto** = más estrés (20% del peso)
- **SDNN bajo** = más estrés (20% del peso)

**Rangos:**
- 0-30: Relajado 😌
- 30-50: Normal 🙂
- 50-70: Estrés moderado 😐
- 70-100: Estrés alto 😰

---

## 📊 Métricas Calculadas

### Dominio Temporal

| Métrica | Descripción | Rango Normal |
|---------|-------------|--------------|
| **HR** | Frecuencia cardíaca media | 60-100 bpm |
| **SDNN** | Desviación estándar de intervalos NN | 50-100 ms |
| **RMSSD** | Variabilidad a corto plazo | 20-50 ms |
| **pNN50** | % intervalos que difieren >50ms | 5-20% |
| **RR medio** | Intervalo promedio entre latidos | 600-1000 ms |

### Dominio Frecuencial

| Métrica | Descripción | Qué Indica |
|---------|-------------|------------|
| **LF Power** | Potencia baja frecuencia (0.04-0.15 Hz) | Sistema simpático (estrés) |
| **HF Power** | Potencia alta frecuencia (0.15-0.4 Hz) | Sistema parasimpático (relajación) |
| **LF/HF Ratio** | Balance simpático/parasimpático | < 1 = relajado, > 2 = estresado |
| **LF nu** | LF normalizado | % de activación |
| **HF nu** | HF normalizado | % de relajación |

### Visualizaciones

1. **ECG Procesado**: Señal cardíaca con picos R visibles
2. **Gráfico de Poincaré**: RRn vs RRn+1 (muestra variabilidad)
3. **Histograma R-R**: Distribución de intervalos
4. **Espectro de Frecuencias**: Bandas VLF, LF, HF

---

## 🛠️ Tecnologías Utilizadas

### Backend (Python)
- **Flask 3.0+**: Servidor web
- **NeuroKit2**: Procesamiento y análisis de señales ECG
- **NumPy**: Operaciones numéricas
- **SciPy**: Procesamiento de señales y análisis frecuencial
- **OpenCV**: Procesamiento de imágenes
- **PyMuPDF (fitz)**: Extracción de imágenes desde PDF
- **Matplotlib**: Generación de gráficos

### Frontend
- **HTML5**: Estructura semántica
- **CSS3**: Estilos modernos con animaciones
- **JavaScript ES6+**: Lógica interactiva
- **Fetch API**: Comunicación con el backend

---

## 📁 Estructura del Proyecto

```
HRV/
│
├── app.py                      # Servidor Flask principal
├── ecg_processor.py            # Extracción de señal ECG desde imagen/PDF
├── hrv_analyzer.py             # Cálculo de métricas HRV y estrés
├── requirements.txt            # Dependencias Python
├── README.md                   # Esta documentación
│
├── static/                     # Archivos estáticos
│   ├── css/
│   │   └── style.css          # Estilos CSS con animaciones
│   └── js/
│       └── main.js            # JavaScript con modales y lógica
│
├── templates/
│   └── index.html             # Página principal HTML
│
└── uploads/                   # Carpeta temporal (se crea automáticamente)
```

### Descripción de Archivos Clave

#### `app.py`
- Servidor Flask
- Endpoints: `/` (home), `/upload` (procesar archivo)
- Orquesta el procesamiento ECG → HRV → JSON

#### `ecg_processor.py`
- Clase `ECGProcessor`
- Métodos principales:
  - `process_file()`: Procesa PDF/imagen
  - `_extract_image_from_pdf()`: Renderiza PDF a imagen
  - `_extract_ecg_signal()`: Detecta señal por color
  - `_detect_ecg_rows()`: Encuentra las 3 filas del gráfico
  - `_resample_signal()`: Interpola a 500 Hz

#### `hrv_analyzer.py`
- Clase `HRVAnalyzer`
- Métodos principales:
  - `analyze()`: Análisis completo HRV
  - `_calculate_time_domain_metrics()`: SDNN, RMSSD, pNN50
  - `_calculate_frequency_domain_metrics()`: LF, HF, ratio
  - `_calculate_stress_index()`: Índice 0-100
  - `generate_poincare_plot()`: Gráfico de Poincaré
  - `generate_rr_histogram()`: Histograma
  - `generate_frequency_plot()`: Espectro

#### `static/js/main.js`
- Base de datos de información de métricas (`metricInfo`)
- Lógica de upload y procesamiento
- Gestión de modales informativos
- Animaciones dinámicas (corazón, gauge)
- Determinación de estados (✅⚠️🔴)

---

## 🐛 Troubleshooting

### Error: "No module named 'flask'"
**Solución:** Instala Flask
```bash
pip install flask
```

### Error al instalar `numpy` en Python 3.14
**Causa:** Python 3.14 es muy nuevo, algunas librerías no tienen binarios precompilados

**Solución:** Instala solo binarios
```bash
pip install numpy --only-binary :all:
```

### Error: "No se pudo extraer la señal ECG"
**Causas posibles:**
1. El PDF/imagen no contiene un gráfico ECG visible
2. El color del ECG no es naranja (ajustar `orange_lower`/`upper` en `ecg_processor.py`)
3. La calidad de la imagen es muy baja

**Solución:** Asegúrate de:
- Usar archivos de Samsung Health Monitor u otros ECGs naranjas
- Que la imagen tenga buena resolución
- Que el gráfico sea visible

### El servidor no inicia en el puerto 5000
**Causa:** Puerto ocupado por otra aplicación

**Solución:** Cambia el puerto en `app.py`
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Usar puerto 5001
```

### Los gráficos no se muestran
**Causa:** matplotlib no genera las imágenes correctamente

**Solución:** Reinstala matplotlib
```bash
pip uninstall matplotlib
pip install matplotlib --only-binary :all:
```

### Modal no se abre al hacer clic en ℹ️
**Causa:** JavaScript no se cargó correctamente

**Solución:**
1. Abre la consola del navegador (F12)
2. Busca errores en la pestaña "Console"
3. Recarga la página (Ctrl+F5)

---

## 📄 Licencia

Este proyecto es de código abierto y está disponible bajo la licencia MIT.

---

## 🙏 Agradecimientos

- **NeuroKit2**: Por la excelente librería de procesamiento ECG
- **Samsung Health Monitor**: Por generar ECGs accesibles
- **Comunidad científica**: Por la investigación en HRV

---

## 📞 Soporte

Si tienes problemas:
1. Revisa la sección [Troubleshooting](#troubleshooting)
2. Verifica que todas las dependencias estén instaladas
3. Asegúrate de usar Python 3.10+

---

## 🔮 Futuras Mejoras

- [ ] Soporte para más formatos de ECG
- [ ] Exportar resultados a PDF
- [ ] Histórico de mediciones
- [ ] Comparación de análisis
- [ ] API REST para integración
- [ ] Modo claro/oscuro conmutable

---

**¡Disfruta analizando tu HRV y conociendo tu nivel de estrés!** ❤️📊
