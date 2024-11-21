import face_recognition
import numpy as np
from PIL import Image
import io

def load_known_faces_from_db(db_results):
    known_faces = []
    for name, image_data in db_results:
        image = Image.open(io.BytesIO(image_data))
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
    return known_faces

def recognize_face_in_image(image_file):
    image = Image.open(image_file.stream).convert("RGB")
    image_np = np.array(image)
    return face_recognition.face_encodings(image_np)
