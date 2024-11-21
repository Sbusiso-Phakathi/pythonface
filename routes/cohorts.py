from flask import Blueprint, request, jsonify
from utils.database import get_db_connection

cohorts_bp = Blueprint('cohorts', __name__)

@cohorts_bp.route('/cohorts', methods=['POST'])
def cohorts():
    cohortname = request.form.get('cohortname')
    siteid = request.form.get('siteid')

    if not cohortname or not siteid:
        return jsonify({"error": "Name and ID are required"}), 400

    try:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            '''INSERT INTO cohorts (cohortname, site_id)
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
