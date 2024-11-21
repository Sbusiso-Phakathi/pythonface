from flask import Blueprint, request, jsonify
from utils.database import get_db_connection

learnersc_bp = Blueprint('lbycohort', __name__)

@learnersc_bp.route('/learners/cohort/<int:cohort_id>', methods=['GET'])
def get_learners_by_cohort(cohort_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute('''SELECT lr.learner_id, lr.name, lr.surname, st.sitename, ch.cohortname, lr.lid, lr.email
                       FROM learners as lr
                       JOIN cohorts as ch using(cohort_id) 
                       JOIN sites as st using(site_id)
                       WHERE lr.cohort_id = %s''', (cohort_id,))
    
    rows = cursor.fetchall()

    data = [
        {
            "id": row[0],
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
