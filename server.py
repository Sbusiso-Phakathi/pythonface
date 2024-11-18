import os
from flask import Flask, request, jsonify, redirect, render_template
from flask_cors import CORS
import face_recognition
from PIL import Image
import numpy as np
import io, requests
import psycopg2

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:5175"}})

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

try:
    conn = get_db_connection()
    cur = conn.cursor()
        
    query = "SELECT name, image_data FROM movies2;"
    cur.execute(query)
    results = cur.fetchall()

    for result in results:
        if result:
            name = result[0]
            image_data = result[1]

            image = Image.open(io.BytesIO(image_data))

            if image.mode == "RGBA":
                image = image.convert("RGB")
            
        known_image = np.array(image)
        encoding = face_recognition.face_encodings(known_image)

        if encoding:
            known_faces.append({
                    "name": name,
                    "encoding": encoding[0]
                })
except Exception as e:
        print(f"Error: {e}")
finally:
    if conn:
        cur.close()
        conn.close()

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
                break  
       
        if not matched:
            faces_data.append({
                "location": {"top": "bad", "right": "bad", "bottom": "bad", "left": "bad"},
                "name": "Unknown"
            })
    
    return jsonify({"faces": faces_data})


@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    image_file = request.files['image']

    image_data = image_file.read()
    name = request.form.get('name') 
    user_id = request.form.get('id')  
    print(name)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute('''INSERT INTO movies2 (name, id, image_data) VALUES (%s, %s, %s)''', (name, user_id, psycopg2.Binary(image_data),))

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({"message": "Image uploaded successfully!"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5002)