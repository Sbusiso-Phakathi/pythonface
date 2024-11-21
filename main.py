from flask import Flask
from flask_cors import CORS  # Import CORS
from routes.face_recognition import face_recognition_bp
from routes.cohorts import cohorts_bp
from routes.learners import learners_bp
from routes.lbycohort import learnersc_bp

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Enable CORS for specific origins (e.g., frontend URL)
CORS(app, resources={r"/*": {"origins": "http://localhost:5175"}})

# Register Blueprints
app.register_blueprint(face_recognition_bp)
app.register_blueprint(cohorts_bp)
app.register_blueprint(learners_bp)
app.register_blueprint(learnersc_bp)

if __name__ == '__main__':
    app.run(debug=True, port=5002)
