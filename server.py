import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import face_recognition
from PIL import Image
import numpy as np
import io
import psycopg2
from datetime import date, datetime
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "http://localhost:5173"}})

known_faces = []

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME"),
        user=os.environ.get("DB_USER"),
        port=os.environ.get("DB_PORT"),
        password=os.environ.get("DB_PASSWORD")
    )

def load_known_faces():
    global known_faces
    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT name, image_data FROM learners;")
        results = cur.fetchall()

        for name, image_data in results:
            image = Image.open(io.BytesIO(image_data))
            print(image)


            if image.mode == "RGBA":
                image = image.convert("RGB")

            known_image = np.array(image)

            encoding = face_recognition.face_encodings(known_image)
            if encoding:
                known_faces.append({
                    "name": name,
                    "encoding": encoding[0],
                    "image": image_data,
                })

    except Exception as e:
        print(f"Error loading known faces: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/recognize-face', methods=['POST'])
def recognize_face():
    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    image_file = request.files['image']
    image = Image.open(image_file.stream).convert("RGB")
    image_np = np.array(image)

    unknown_encodings = face_recognition.face_encodings(image_np)

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
                            '''INSERT INTO admin (name, userid, date, datetime, cohort_id)
                               VALUES (%s, %s, %s, %s, %s)''',
                            (known_face['name'], 1, current_date, current_datetime, 11)
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

@app.route('/cohorts', methods=['POST'])
def cohorts():

    cohortname = request.form.get('cohortname')
    siteid = request.form.get('siteid')


    if not cohortname or not siteid:
        return jsonify({"error": "Name and ID are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            '''INSERT INTO cohorts ( cohortname, site_id)
               VALUES (%s, %s)''',
            (cohortname, int(siteid))
        )
        conn.commit()

        return jsonify({"message": "Cohort added..."}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

@app.route('/upload-image', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return jsonify({"error": "No image part in the request"}), 400

    image_file = request.files['image']
    name = request.form.get('name')
    surname = request.form.get('surname')
    lid = request.form.get('lid')
    cohort = request.form.get('cohort')
    email = request.form.get('email')

    if not name:
        return jsonify({"error": "Name and ID are required"}), 400

    try:
        image_data = image_file.read()
        conn = get_db_connection()
        cur = conn.cursor()
        print('dfscds')

        cur.execute(
            '''INSERT INTO learners ( name, surname, lid, cohort_id, email, image_data)
               VALUES (%s, %s, %s, %s, %s, %s)''',
            (name, surname, int(lid), int(cohort), email, psycopg2.Binary(image_data))
        )

        conn.commit()

        return jsonify({"name": name}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

load_known_faces()

@app.route('/learners', methods=['GET'])
def get_data():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT lr.learner_id, lr.name, lr.surname, st.sitename, ch.cohortname, lr.lid, lr.email FROM learners as lr
                        join cohorts as ch  using(cohort_id) 
                        join sites as st using(site_id) ''')
    rows = cursor.fetchall()

    cursor.execute('''SELECT cohortname from cohorts''')
    rows2 = cursor.fetchall()

    cursor.execute('''SELECT cohort_id from cohorts''')
    rows3 = cursor.fetchall()

    cursor.execute('''SELECT ch.cohortname, COUNT(*) AS learner_count
                    FROM learners AS lr
                    JOIN cohorts AS ch ON lr.cohort_id = ch.cohort_id
                    GROUP BY ch.cohort_id, ch.cohortname;''')
    rows4 = cursor.fetchall()

    print(rows4)

    all = [item[0] for item in rows2]
    allids = [item[0] for item in rows3]
    # Transforming the data into a JSON-friendly format
    data = [
        {
            "id" : row[0],
            "name": row[1],
            "surname": row[2],
            "site": row[3],
            "cohort": row[4],
            "lid": row[5],
            "email": row[6],
            "all": all,
            "allids": allids
        }
        for row in rows
    ]

    cursor.close()
    connection.close()

    return jsonify(data)

@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query', '')
    if not query:
        return jsonify({"error": "Search query is required"}), 400

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''
        SELECT lr.learner_id, lr.name, lr.surname, st.sitename, ch.cohortname, lr.lid, lr.email FROM learners as lr
                        join cohorts as ch  using(cohort_id) 
                        join sites as st using(site_id) 
        WHERE lr.name ILIKE %s OR lr.email ILIKE %s OR lr.surname ILIKE %s
    ''', (f'%{query}%',f'%{query}%',f'%{query}%'))

    rows = cursor.fetchall()
    data = [
        { "id" : row[0],
            "name": row[1],
            "surname": row[2],
            "site": row[3],
            "cohort": row[4],
            "lid": row[5],
            "email": row[6]}
        for row in rows
    ]

    cursor.close()
    connection.close()

    return jsonify(data)

@app.route('/users/<int:id>', methods=['GET'])
def users(id):
    connection = get_db_connection()
    cursor = connection.cursor()
    if id != 5000:
        cursor.execute('''SELECT lr.learner_id, lr.name, lr.surname, st.sitename, ch.cohortname, lr.lid, lr.email  FROM learners as lr
                        join cohorts as ch  using(cohort_id) 
                    join sites as st using(site_id) where cohort_id=%s''',(id,))
    else:
        cursor.execute('''SELECT lr.learner_id, lr.name, lr.surname, st.sitename, ch.cohortname, lr.lid, lr.email  FROM learners as lr
                        join cohorts as ch  using(cohort_id) 
                    join sites as st using(site_id)''')
    rows = cursor.fetchall()

    # Transforming the data into a JSON-friendly format
    data = [
        {
            "id" : row[0],
            "name": row[1],
            "surname": row[2],
            "site": row[3],
            "cohort": row[4],
            "lid": row[5],
            "email": row[6],
        }
        for row in rows
    ]

    cursor.close()
    connection.close()

    return jsonify(data)

@app.route('/data', methods=['GET'])
def get_data_for_date():
    print('fvdf')
    date = request.args.get('date')  # Get date from the query parameters (e.g., YYYY-MM-DD)
    cohort = request.args.get('cohort')
    if not date:
        return jsonify({"error": "Date is required"}), 400

    try:
        # Validate the date format
        datetime.strptime(date, "%Y-%m-%d")
        
        # Connect to the PostgreSQL database
        conn = get_db_connection()
        cursor = conn.cursor()

        # Query the database for records that match the selected date
        cursor.execute("SELECT * FROM admin WHERE date = %s and cohort_id = %s", (date,cohort,))

        # Fetch the results
        rows = cursor.fetchall()

        data = [
        {
            "id" : row[0],
            "name": row[1],
            "surname": row[2],
            "site": row[3],
            "cohort": row[4],
            "lid": row[4],
            "email": row[3],
        }
        for row in rows
    ]

        # Close the database connection
        cursor.close()
        conn.close()

        # Return the results as JSON
        return jsonify(data)

    except psycopg2.Error as e:
        return jsonify({"error": str(e)}), 500
    except ValueError:
        return jsonify({"error": "Invalid date format"}), 400

@app.route('/delet/<int:id>', methods=['DELETE'])
def delet(id):
    data = []
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM learners where learner_id = %s", (id,))
    data.append({
                        "status": "ok",
                    })
    # Transforming the data into a JSON-friendly format
    connection.commit()

    cursor.close()
    connection.close()

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True, port=5002)