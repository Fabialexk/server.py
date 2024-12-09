from flask import Flask, request, send_file, jsonify, render_template_string
from flask_cors import CORS
from werkzeug.utils import secure_filename
import os
import pdfplumber
import pandas as pd

app = Flask(__name__)
CORS(app)

# Configuración
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'analisis-de-salario', 'uploads')
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# HTML Template actualizado
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,200..800&family=Jost:ital,wght@0,100..900;1,100..900&family=Montserrat:ital,wght@0,100..900;1,100..900&display=swap" rel="stylesheet">

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Análisis de salario - Convertidor PDF a Excel</title>
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f4f4f4;
            margin: 0;
            padding: 0;
        }

        nav#navigation {
            background-color: #333;
            padding: 1rem;
        }

        nav .wrapper {
            display: flex;
            justify-content: space-between;
            align-items: center;
            max-width: 1200px;
            margin: 0 auto;
        }

        .logo img {
            height: 40px;
        }

        .container {
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 80vh;
            padding: 40px 20px;
        }

        .drop-area {
            display: flex;
            border: 3px dashed #a2a2a2;
            border-radius: 20px;
            text-align: center;
            padding: 200px 300px;
            transition: all 0.3s ease;
            background-color: white;
            margin-bottom: 20px;
        }

        .drop-area.drag-over {
            background-color: #eaf3ff;
            border-color: #629eff;
        }

        .drop-content {
            display: flex;
            flex-direction: column;
            align-items: center;
        }

        .upload-icon {
            color: #a2a2a2;
            margin-bottom: 20px;
        }

        .drop-content h2 {
            color: #666;
            margin-bottom: 10px;
        }

        .select-btn {
            font-size: 20px;
            background-color: #008F4E;
            color: white;
            border: none;
            padding: 15px 100px;
            border-radius: 15px;
            cursor: pointer;
            margin-top: 10px;
            transition: background-color 0.3s ease;
        }

        .select-btn:hover {
            background-color: #00a75c;
        }

        #status {
            margin-top: 20px;
            padding: 10px;
            border-radius: 4px;
            text-align: center;
        }

        .error {
            background-color: #ffebee;
            color: #c62828;
        }

        .success {
            background-color: #e8f5e9;
            color: #2e7d32;
        }

        footer {
            background-color: #333;
            color: white;
            padding: 2rem 0;
            margin-top: auto;
        }

        footer .wrapper {
            max-width: 1200px;
            margin: 0 auto;
            padding: 0 20px;
        }

        footer .content {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 2rem;
        }

        @media (max-width: 480px) {
            .drop-area {
                padding: 100px 50px;
            }

            .select-btn {
                font-size: 16px;
                padding: 8px 60px;
                width: 100%;
                max-width: 300px;
            }
        }
    </style>
</head>
<body>
    <nav id="navigation">
        <div class="wrapper">
            <a class="logo" href="../index.html">
                <img src="../assets/LOGO COUNTER.png" alt="">
            </a>
            
            <div class="menu">
                <ul>
                    <li><a onclick="closeMenu()" href="/index.html">Volver a la página principal</a></li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container">
        <div class="drop-area">
            <form id="uploadForm" class="drop-content">
                <img src="data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='50' height='50' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round' class='lucide lucide-upload'><path d='M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4'/><polyline points='17 8 12 3 7 8'/><line x1='12' x2='12' y1='3' y2='15'/></svg>" alt="Upload Icon" class="upload-icon">
                
                <h2>Arrastra y suelta tu PDF aquí</h2>
                <p>O</p>
                <input type="file" accept=".pdf" required id="pdfFile" hidden>
                <button type="button" onclick="document.getElementById('pdfFile').click()" class="select-btn">Selecciona tu PDF</button>
                <button type="submit" class="select-btn" style="margin-top: 20px;">Convertir a Excel</button>
            </form>
        </div>
        <div id="status"></div>
    </div>

    <footer id="footer">
        <div class="wrapper">
            <div class="content">
                <div class="navigation">
                    <h3>Navegación</h3>
                    <p><a href="#home">Inicio</a></p>
                    <p><a href="#downloads-section">Sobre nosotros</a></p>
                    <p><a href="#sobre">Subir PDF</a></p>
                    <p><a href="#contato">Contacto</a></p>
                </div>

                <div class="contato">
                    <h3>Contacte con Nosotros</h3>
                    <p><a target="_blank" href="tel:+529511285796">+52 951-128-5796</a></p>
                    <p><a target="_blank" href="tel:+529516523110">+52 951-652-3110</a></p>
                </div>

                <div class="redes-sociais">
                    <h3>Social</h3>
                    <div class="icons">
                        <a target="_blank" href="https://api.whatsapp.com/send?phone=9516523110">WhatsApp</a>
                        <a target="_blank" href="https://www.instagram.com/fabialexk_mz/?hl=es">Instagram</a>
                    </div>
                </div>
            </div>
        </div>
    </footer>

    <script>
        document.getElementById('uploadForm').addEventListener('submit', async (e) => {
            e.preventDefault();
            
            const statusDiv = document.getElementById('status');
            const fileInput = document.getElementById('pdfFile');
            const file = fileInput.files[0];
            
            if (!file) {
                statusDiv.textContent = 'Por favor selecciona un archivo PDF';
                statusDiv.className = 'error';
                return;
            }

            if (!file.name.toLowerCase().endsWith('.pdf')) {
                statusDiv.textContent = 'Por favor selecciona un archivo PDF válido';
                statusDiv.className = 'error';
                return;
            }

            statusDiv.textContent = 'Procesando archivo...';
            statusDiv.className = '';

            const formData = new FormData();
            formData.append('file', file);

            try {
                const response = await fetch('/api/convert-pdf', {
                    method: 'POST',
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error en el servidor');
                }

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = file.name.replace('.pdf', '.xlsx');
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
                
                statusDiv.textContent = 'Archivo convertido exitosamente';
                statusDiv.className = 'success';
                
            } catch (error) {
                console.error('Error:', error);
                statusDiv.textContent = `Error: ${error.message}`;
                statusDiv.className = 'error';
            }
        });

        // Drag and drop functionality
        const dropArea = document.querySelector('.drop-area');
        const fileInput = document.getElementById('pdfFile');

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults (e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropArea.classList.add('drag-over');
        }

        function unhighlight(e) {
            dropArea.classList.remove('drag-over');
        }

        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            const dt = e.dataTransfer;
            const files = dt.files;
            fileInput.files = files;
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/convert-pdf', methods=['POST'])
def convert_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No se envió ningún archivo"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No se seleccionó ningún archivo"}), 400
        
        if not file.filename.lower().endswith('.pdf'):
            return jsonify({"error": "Solo se aceptan archivos PDF"}), 400
        
        filename = secure_filename(file.filename)
        pdf_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(pdf_path)
        
        text_data = []
        with pdfplumber.open(pdf_path) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_data.extend([{'Página': page_num, 'Contenido': line.strip()} for line in text.split('\n') if line.strip()])
        
        df = pd.DataFrame(text_data)
        excel_path = os.path.join(UPLOAD_FOLDER, f"{os.path.splitext(filename)[0]}.xlsx")
        
        with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Contenido')
            workbook = writer.book
            worksheet = writer.sheets['Contenido']
            for idx, col in enumerate(df.columns):
                worksheet.set_column(idx, idx, max(len(col) + 2, df[col].astype(str).str.len().max() + 2))
        
        return send_file(
            excel_path,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{os.path.splitext(filename)[0]}.xlsx"
        )

    except Exception as e:
        return jsonify({"error": f"Error al procesar el archivo: {str(e)}"}), 500
    
    finally:
        try:
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            if os.path.exists(excel_path):
                os.remove(excel_path)
        except Exception:
            pass

if __name__ == '__main__':
    print("Servidor iniciando en http://localhost:8000")
    app.run(host='0.0.0.0', port=8000, debug=True)