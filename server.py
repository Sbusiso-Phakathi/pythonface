# # server.py
# import os
# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import face_recognition
# from PIL import Image
# import numpy as np
# import io, requests

# app = Flask(__name__)
# CORS(app) 

# @app.route('/recognize-face', methods=['POST'])
# def recognize_face():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image provided"}), 400

#     image_file = request.files['image']
#     image = Image.open(image_file.stream)
#     image_np = np.array(image)

#     unknown_encodings = face_recognition.face_encodings(image_np)

#     username = os.environ.get('USER')
#     image_url = "https://github.com/Sbusiso-Phakathi/recruit/blob/main/sbusisophakathi.jpg?raw=true"

#     response = requests.get(image_url)
#     if response.status_code == 200:
#         image = Image.open(io.BytesIO(response.content))
        
#         if image.mode == "RGBA":
#             image = image.convert("RGB")
        
#         known_image = np.array(image)
#     known_encoding = face_recognition.face_encodings(known_image)[0]
#     faces_data = []

#     if unknown_encodings:
#         unknown_encoding = unknown_encodings[0]
                        
#         results = face_recognition.compare_faces([known_encoding], unknown_encoding, tolerance=0.39)
                        
#         if results[0]:
           
#             faces_data.append({
#                             "location": {"top": "ok", "right": "ok", "bottom": "ok", "left": "ok"},
#                         })
#         else:
#             faces_data.append({
#                             "location": {"top": "bad", "right": "bad", "bottom": "bad", "left": "bad"},
#                         })
            
#     return jsonify({"faces": faces_data})

# if __name__ == '__main__':
#     app.run(debug=True, port=5002)


import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
from PIL import Image
import numpy as np
import io, requests

app = Flask(__name__)
CORS(app)

# List of known faces, you can add names and image URLs for 10 people
known_faces = []

# Function to add known faces to the system
def add_known_face(image_url, name="Unknown"):
    response = requests.get(image_url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))

        if image.mode == "RGBA":
            image = image.convert("RGB")
        
        known_image = np.array(image)
        encoding = face_recognition.face_encodings(known_image)

        if encoding:
            known_faces.append({
                "name": name,
                "encoding": encoding[0]
            })

# Add your known faces here
known_face_urls = [
    ("https://github.com/Sbusiso-Phakathi/recruit/blob/main/sbusisophakathi.jpg?raw=true", "Sbusiso"),
    ("https://github.com/Sbusiso-Phakathi/recruit/blob/main/bonolo.jpg?raw=true", "Phakathi"),
    ("https://github.com/Sbusiso-Phakathi/recruit/blob/main/murendeni.jpg?raw=true", "Murendeni"),
]

# Add all 10 known faces
for url, name in known_face_urls:
    add_known_face(url, name)

@app.route('/recognize-face', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream)
    image_np = np.array(image)

    unknown_encodings = face_recognition.face_encodings(image_np)

    faces_data = []

    if unknown_encodings:
        unknown_encoding = unknown_encodings[0]
        
        # Compare the unknown encoding to each known encoding
        matched = False
        for known_face in known_faces:
            results = face_recognition.compare_faces([known_face["encoding"]], unknown_encoding, tolerance=0.39)
            
            if results[0]:
                print(unknown_encoding)
                print(known_face)
                faces_data.append({
                    "location": {"top": "ok", "right": "ok", "bottom": "ok", "left": "ok"},
                    "name": known_face["name"]
                })
                matched = True
                break  # Stop after the first match
       
        if not matched:
            faces_data.append({
                "location": {"top": "bad", "right": "bad", "bottom": "bad", "left": "bad"},
                "name": "Unknown"
            })
    
    return jsonify({"faces": faces_data})

if __name__ == '__main__':
    app.run(debug=True, port=5002)
