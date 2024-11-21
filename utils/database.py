import psycopg2
from config import Config

def get_db_connection():
    return psycopg2.connect(
        host=Config.DB_HOST,
        database=Config.DB_NAME,
        user=Config.DB_USER,
        port=Config.DB_PORT,
        password=Config.DB_PASSWORD
    )
