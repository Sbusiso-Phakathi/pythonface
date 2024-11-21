from flask import Blueprint, request, jsonify
from utils.database import get_db_connection

learners_bp = Blueprint('learners', __name__)

@learners_bp.route('/learners', methods=['GET'])
def get_learners():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute('''SELECT lr.learner_id, lr.name, lr.surname, st.sitename, ch.cohortname, lr.lid, lr.email FROM learners as lr
                        join cohorts as ch using(cohort_id) 
                        join sites as st using(site_id)''')
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

    all_cohorts = [item[0] for item in rows2]
    all_cohort_ids = [item[0] for item in rows3]

    data = [
        {
            "id" : row[0],
            "name": row[1],
            "surname": row[2],
            "site": row[3],
            "cohort": row[4],
            "lid": row[5],
            "email": row[6],
            "all": all_cohorts,
            "allids": all_cohort_ids
        }
        for row in rows
    ]

    cursor.close()
    connection.close()

    return jsonify(data)
