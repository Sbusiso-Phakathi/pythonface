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
from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
import face_recognition
from PIL import Image
import numpy as np
import io, requests
import psycopg2

app = Flask(__name__)
# CORS(app)
CORS(app, resources={r"/*": {"origins": "http://localhost:5175"}})

# List of known faces, you can add names and image URLs for 10 people
known_faces = []

def get_db_connection():
    conn = psycopg2.connect(
        host="localhost",
        database="todo",
        user="postgres",
        port=5430,
        password=""
    )
    return conn

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
    ("https://github.com/Sbusiso-Phakathi/recruit/blob/main/abbie.jpg?raw=true", "Abbie"),
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

# @app.route('/add', methods=['POST'])
# def add():
#     # Get form data
#     data = request.get_json()
#     name = data.get('name')
#     id = data.get('id')
#     # print(name)
#     # Connect to the database and insert data
#     conn = get_db_connection()
#     cur = conn.cursor()
#     cur.execute("INSERT INTO movies2 (name, id) VALUES (%s, %s)", (name, id))
#     conn.commit()
#     cur.close()
#     conn.close()

#     return "hyuhgu"


@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    image_file = request.files['image']

    # Read the image data as bytes
    image_data = image_file.read()
    name = request.form.get('name')  # Get additional data
    user_id = request.form.get('id')  # Get additional data
    print(name)

    try:
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cur = conn.cursor()

        # Insert the image into the database as BYTEA (binary data)
        cur.execute('''INSERT INTO movies2 (name, id, image_data) VALUES (%s, %s, %s)''', (name, user_id, psycopg2.Binary(image_data),))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Image uploaded successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)
