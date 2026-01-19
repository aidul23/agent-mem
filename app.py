# app.py
import os
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from auth_and_profile import get_or_create_user, set_user_consent
from agent import run_agent_turn
from enterprise_memory import EnterpriseMemoryManager
from document_ingestion import DocumentIngestion
from memory_reflection import UpdateTracker

app = Flask(__name__, static_folder="static")
CORS(app)  # Enable CORS for frontend

# Enterprise setup
HINDSIGHT_BASE_URL = os.environ.get("HINDSIGHT_BASE_URL", "http://localhost:8888")
COMPANY_ID = os.environ.get("COMPANY_ID", "default-company")
UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "./uploads")
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'md', 'docx'}

# Create upload folder if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize enterprise memory manager
memory_manager = EnterpriseMemoryManager(HINDSIGHT_BASE_URL, COMPANY_ID)


@app.route("/")
def index():
    return send_from_directory("static", "index.html")


@app.route("/admin")
def admin():
    return send_from_directory("static", "admin.html")


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
        product_id = data.get("product_id")
        department = data.get("department")
        
        if not message:
            return jsonify({"error": "Message is required"}), 400
        
        reply = run_agent_turn(user_id, message, product_id, department)
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


@app.get("/admin/verify-token")
def verify_token():
    """Verify admin token without performing any action"""
    try:
        auth_token = request.headers.get("Authorization", "")
        expected_token = os.environ.get('ADMIN_TOKEN', 'admin-secret')
        expected_auth = f"Bearer {expected_token}"
        
        if not auth_token or auth_token.strip() != expected_auth:
            return jsonify({"valid": False, "error": "Invalid token"}), 401
        
        return jsonify({"valid": True, "message": "Token is valid"})
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500


# Admin endpoints for enterprise features
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.post("/admin/ingest-document")
def ingest_document():
    """Admin endpoint to ingest company documents"""
    try:
        # Simple auth check (in production, use proper authentication)
        auth_token = request.headers.get("Authorization", "")
        expected_token = os.environ.get('ADMIN_TOKEN', 'admin-secret')
        expected_auth = f"Bearer {expected_token}"
        
        if not auth_token or auth_token.strip() != expected_auth:
            return jsonify({"error": "Unauthorized - Invalid admin token"}), 401
        
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": f"File type not allowed. Allowed: {ALLOWED_EXTENSIONS}"}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Get metadata
        document_type = request.form.get('type', 'dfx_rule')
        version = request.form.get('version', '1.0')
        importance = request.form.get('importance', 'high')
        
        # Ingest document
        company_kb = memory_manager.get_company_kb()
        ingestion = DocumentIngestion(company_kb)
        chunks = ingestion.ingest_document(
            file_path=filepath,
            document_type=document_type,
            version=version,
            importance=importance
        )
        
        return jsonify({
            "status": "success",
            "chunks_ingested": chunks,
            "filename": filename
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/admin/ingest-text")
def ingest_text():
    """Admin endpoint to ingest text content directly"""
    try:
        auth_token = request.headers.get("Authorization", "")
        expected_token = os.environ.get('ADMIN_TOKEN', 'admin-secret')
        expected_auth = f"Bearer {expected_token}"
        
        if not auth_token or auth_token.strip() != expected_auth:
            return jsonify({"error": "Unauthorized - Invalid admin token"}), 401
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json() or {}
        content = data.get("content", "")
        document_type = data.get("type", "dfx_rule")
        version = data.get("version", "1.0")
        importance = data.get("importance", "high")
        source = data.get("source", "manual_input")
        
        if not content:
            return jsonify({"error": "Content is required"}), 400
        
        # Ingest text
        company_kb = memory_manager.get_company_kb()
        ingestion = DocumentIngestion(company_kb)
        chunks = ingestion.ingest_document(
            file_path=source,
            document_type=document_type,
            version=version,
            importance=importance,
            content=content
        )
        
        return jsonify({
            "status": "success",
            "chunks_ingested": chunks
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/admin/update-rule")
def update_rule():
    """Update a company rule"""
    try:
        auth_token = request.headers.get("Authorization", "")
        expected_token = os.environ.get('ADMIN_TOKEN', 'admin-secret')
        expected_auth = f"Bearer {expected_token}"
        
        if not auth_token or auth_token.strip() != expected_auth:
            return jsonify({"error": "Unauthorized - Invalid admin token"}), 401
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json() or {}
        rule_id = data.get("rule_id")
        new_content = data.get("content", "")
        new_version = data.get("version", "1.0")
        change_summary = data.get("summary", "")
        
        if not rule_id or not new_content:
            return jsonify({"error": "rule_id and content are required"}), 400
        
        company_kb = memory_manager.get_company_kb()
        tracker = UpdateTracker(company_kb)
        tracker.update_rule(
            rule_id=rule_id,
            new_content=new_content,
            new_version=new_version,
            change_summary=change_summary
        )
        
        return jsonify({"status": "success", "rule_id": rule_id, "version": new_version})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.post("/admin/reflect")
def reflect():
    """Trigger reflection on a topic"""
    try:
        auth_token = request.headers.get("Authorization", "")
        expected_token = os.environ.get('ADMIN_TOKEN', 'admin-secret')
        expected_auth = f"Bearer {expected_token}"
        
        if not auth_token or auth_token.strip() != expected_auth:
            return jsonify({"error": "Unauthorized - Invalid admin token"}), 401
        
        if not request.is_json:
            return jsonify({"error": "Request must be JSON"}), 400
        
        data = request.get_json() or {}
        topic = data.get("topic", "")
        bank_type = data.get("bank_type", "company")  # company, product, department
        
        if not topic:
            return jsonify({"error": "topic is required"}), 400
        
        from memory_reflection import MemoryReflection
        
        if bank_type == "company":
            memory = memory_manager.get_company_kb()
        elif bank_type == "product":
            product_id = data.get("product_id")
            if not product_id:
                return jsonify({"error": "product_id required for product bank"}), 400
            memory = memory_manager.get_product_kb(product_id)
        else:
            return jsonify({"error": "Invalid bank_type"}), 400
        
        reflection = MemoryReflection(memory)
        result = reflection.reflect_and_summarize(topic)
        
        return jsonify({
            "status": "success",
            "reflection": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(port=5001, debug=True, host="0.0.0.0")

