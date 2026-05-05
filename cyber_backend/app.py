from flask import Flask, jsonify, request
from flask_cors import CORS
import mysql.connector
import os

app = Flask(__name__)
CORS(app)

# MySQL Connection — credentials loaded from environment variables
# Set these before running: DB_HOST, DB_USER, DB_PASSWORD, DB_NAME
db = mysql.connector.connect(
    host=os.environ.get("DB_HOST", "127.0.0.1"),
    user=os.environ.get("DB_USER", "root"),
    password=os.environ.get("DB_PASSWORD", ""),
    database=os.environ.get("DB_NAME", "cyber_threat_detection")
)

cursor = db.cursor()

@app.route("/")
def home():
    return jsonify({"message": "Cyber Threat Detection Backend Running Successfully!"})


# USB LOG API
@app.route("/api/usb-log", methods=["POST"])
def add_usb_log():
    data = request.json

    usb_device_id = data.get("usb_device_id")
    device_name = data.get("device_name")
    vendor_name = data.get("vendor_name")
    action_taken = data.get("action_taken")
    session_start = data.get("session_start")
    session_end = data.get("session_end")
    system_user = data.get("system_user")

    query = """
        INSERT INTO usb_logs
        (usb_device_id, device_name, vendor_name, action_taken, session_start, session_end, system_user)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    values = (
        usb_device_id,
        device_name,
        vendor_name,
        action_taken,
        session_start,
        session_end,
        system_user
    )

    cursor.execute(query, values)
    db.commit()

    return jsonify({"message": "USB log stored successfully!"})


if __name__ == "__main__":
    app.run(debug=False)  # Set debug=False in production
