# server.py
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
from PIL import Image
import numpy as np
import io, requests

app = Flask(__name__)
CORS(app) 

@app.route('/recognize-face', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream)
    image_np = np.array(image)

    unknown_encodings = face_recognition.face_encodings(image_np)

    username = os.environ.get('USER')
    image_url = "https://github.com/Sbusiso-Phakathi/recruit/blob/main/sbusisophakathi.jpg?raw=true"

    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        
        if image.mode == "RGBA":
            image = image.convert("RGB")
        
        known_image = np.array(image)
    known_encoding = face_recognition.face_encodings(known_image)[0]
    faces_data = []

    if unknown_encodings:
        unknown_encoding = unknown_encodings[0]
                        
        results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.3)
                        
        if results[0]:
           
            faces_data.append({
                            "location": {"top": "ok", "right": "ok", "bottom": "ok", "left": "ok"},
                        })
        else:
            faces_data.append({
                            "location": {"top": "bad", "right": "bad", "bottom": "bad", "left": "bad"},
                        })
            
    return jsonify({"faces": faces_data})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
