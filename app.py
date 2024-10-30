import os 
import cv2
import numpy as np
from datetime import datetime
from flask import Flask, jsonify, render_template, request, send_file 
from werkzeug.utils import secure_filename

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Função para verificar se a extensão é permitida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/image/<filename>')
def upload_file(filename):
    file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(file)

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return 'Nenhum arquivo selecionado.'

    if file and allowed_file(file.filename):
        # Salva a imagem original
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        server_address = f"{request.scheme}://{request.host}"
        image_url = f"{server_address}/image/{filename}"

        # Carrega a imagem salva em escala de cinza
        gray = cv2.imread(file_path, cv2.IMREAD_GRAYSCALE)

        # Define a profundidade e calcula o gradiente na direção x e y
        ddepth = cv2.CV_16S
        grad_x = cv2.Sobel(gray, ddepth, 1, 0, ksize=3, scale=1)
        grad_y = cv2.Sobel(gray, ddepth, 0, 1, ksize=3, scale=1)

        # Converte para valor absoluto e uint8
        abs_grad_x = cv2.convertScaleAbs(grad_x)
        abs_grad_y = cv2.convertScaleAbs(grad_y)

        # Calcula o gradiente final combinando x e y
        grad = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)

        # Concatena a imagem com a original
        saida = cv2.hconcat((grad, gray))

        # Redimensiona a imagem concatenada em 60%
        saida = cv2.resize(saida, None, fx=0.4, fy=0.4)

        # Gera um nome de arquivo único para salvar a imagem processada
        processed_filename = f"processed_{filename}"
        processed_path = os.path.join(app.config['UPLOAD_FOLDER'], processed_filename)
        cv2.imwrite(processed_path, saida)

        server_address2 = f"{request.scheme}://{request.host}"
        image_url2 = f"{server_address2}/image/{processed_filename}"

        return jsonify({
            "datetime": datetime.now(),
            "image": image_url,
            "image_proc": image_url2,
            "ip": request.remote_addr
        })

    return 'Arquivo não permitido.'

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")
