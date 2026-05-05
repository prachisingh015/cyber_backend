import mysql.connector
import os

def connect_db():
    """
    Creates and returns a fresh MySQL connection.
    Credentials are read from environment variables — never hardcode them.

    Set these environment variables before running the project:
      DB_HOST     (default: localhost)
      DB_USER     (default: root)
      DB_PASSWORD (required — no default)
      DB_NAME     (default: cyber_threat_detection)
    """
    return mysql.connector.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        user=os.environ.get("DB_USER", "root"),
        password=os.environ.get("DB_PASSWORD", ""),
        database=os.environ.get("DB_NAME", "cyber_threat_detection")
    )
