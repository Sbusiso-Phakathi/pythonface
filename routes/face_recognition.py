from flask import Blueprint, request, jsonify
from utils.face_encoding import recognize_face_in_image, load_known_faces_from_db
from utils.database import get_db_connection
import face_recognition
from datetime import date, datetime

face_recognition_bp = Blueprint('face_recognition', __name__)

known_faces = []

def load_known_faces():
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, image_data FROM learners;")
        results = cur.fetchall()
        global known_faces
        known_faces = load_known_faces_from_db(results)
    except Exception as e:
        print(f"Error loading known faces: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

@face_recognition_bp.route('/recognize-face', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    unknown_encodings = recognize_face_in_image(image_file)

    faces_data = []

    if unknown_encodings:
        unknown_encoding = unknown_encodings[0]
        matched = False
        for known_face in known_faces:
            results = face_recognition.compare_faces([known_face["encoding"]], unknown_encoding, tolerance=0.39)
            if results[0]:
                matched = True
                try:
                    conn = get_db_connection()
                    cur = conn.cursor()
                    current_date = date.today()
                    current_datetime = datetime.now()

                    cur.execute(
                        "SELECT datetime FROM admin WHERE name = %s AND date = %s",
                        (known_face['name'], current_date)
                    )
                    result = cur.fetchone()

                    if result is None:
                        cur.execute(
                            '''INSERT INTO admin (name, userid, date, datetime)
                               VALUES (%s, %s, %s, %s)''',
                            (known_face['name'], 1, current_date, current_datetime)
                        )
                        conn.commit()

                    faces_data.append({
                        "status": "ok",
                        "name": known_face["name"],
                        "time": result[0] if result else current_datetime
                    })
                except Exception as e:
                    return jsonify({"error": str(e)}), 500
                finally:
                    if conn:
                        cur.close()
                        conn.close()
                break

        if not matched:
            faces_data.append({
                "status": "bad",
                "name": "Unknown",
            })

    return jsonify({"faces": faces_data})
