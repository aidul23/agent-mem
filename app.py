# app.py
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from auth_and_profile import get_or_create_user, set_user_consent
from agent import run_agent_turn

app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for frontend


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.post("/consent")
def consent():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json() or {}
        user_id = data.get("user_id", "default")
        allow = bool(data.get("allow", False))
        set_user_consent(user_id, allow)
        return jsonify({"status": "ok", "allow_memory": allow})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/chat")
def chat():
    try:
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json() or {}
        user_id = data.get("user_id", "default")
        message = data.get("message", "")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        reply = run_agent_turn(user_id, message)
        profile = get_or_create_user(user_id)
        return jsonify({
            "reply": reply,
            "memory_enabled": profile.allow_memory,
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.get("/user/<user_id>/status")
def user_status(user_id: str):
    profile = get_or_create_user(user_id)
    return jsonify({
        "user_id": profile.user_id,
        "allow_memory": profile.allow_memory,
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok", "service": "gpt-lab-agent"})


if __name__ == "__main__":
    app.run(port=5000, debug=True, host="0.0.0.0")

