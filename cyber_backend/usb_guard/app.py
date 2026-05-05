from flask import Flask, request, jsonify
from security_core import verify_user, is_system_locked

app = Flask(__name__)


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "USB Guard API Running"})


@app.route("/status", methods=["GET"])
def status():
    locked, lock_until = is_system_locked()
    return jsonify({
        "locked": locked,
        "lock_until": str(lock_until) if lock_until else None
    })


@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    password = data.get("password")

    if not password:
        return jsonify({"error": "Password required"}), 400

    result = verify_user(password)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)