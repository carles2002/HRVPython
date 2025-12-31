"""
HRV Analyzer - Aplicacion web para analizar ECG y calcular HRV/estres
"""
import os
import json
import base64
from io import BytesIO
from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename

from ecg_processor import ECGProcessor
from hrv_analyzer import HRVAnalyzer

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No se ha enviado ningun archivo'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No se ha seleccionado ningun archivo'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # Asegurar que existe la carpeta uploads
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
        file.save(filepath)

        try:
            # Procesar el archivo
            results = analyze_ecg(filepath)
            return jsonify(results)
        except Exception as e:
            return jsonify({'error': f'Error procesando archivo: {str(e)}'}), 500
        finally:
            # Limpiar archivo temporal
            if os.path.exists(filepath):
                os.remove(filepath)

    return jsonify({'error': 'Tipo de archivo no permitido. Use PDF, PNG o JPG'}), 400

def analyze_ecg(filepath):
    """Analiza un archivo ECG y devuelve metricas HRV"""

    # 1. Procesar imagen/PDF para extraer senal ECG
    processor = ECGProcessor()
    ecg_signal, sampling_rate, ecg_plot_base64 = processor.process_file(filepath)

    # 2. Analizar HRV
    analyzer = HRVAnalyzer(sampling_rate)
    hrv_results = analyzer.analyze(ecg_signal)

    # 3. Generar visualizaciones
    poincare_plot = analyzer.generate_poincare_plot()
    rr_histogram = analyzer.generate_rr_histogram()
    frequency_plot = analyzer.generate_frequency_plot()

    return {
        'success': True,
        'metrics': hrv_results['metrics'],
        'stress': hrv_results['stress'],
        'plots': {
            'ecg': ecg_plot_base64,
            'poincare': poincare_plot,
            'histogram': rr_histogram,
            'frequency': frequency_plot
        },
        'interpretation': hrv_results['interpretation']
    }

if __name__ == '__main__':
    print("=" * 50)
    print("HRV Analyzer - Servidor iniciado")
    print("Abre http://localhost:5000 en tu navegador")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)
