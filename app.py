from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import logging
import logging.handlers
from datetime import datetime
import os
from dotenv import load_dotenv
from aws_translator import AWSTranslator

# Load environment variables
load_dotenv()

# Configure logging
def setup_logging():
    """Thiết lập logging cho production"""
    log_level = os.environ.get('LOG_LEVEL', 'INFO')
    
    # Tạo thư mục logs nếu chưa có
    log_dir = "/var/log/webhook-app"
    try:
        os.makedirs(log_dir, exist_ok=True)
    except PermissionError:
        # Fallback to current directory if no permission
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
    
    # Cấu hình logging
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler với rotation
            logging.handlers.RotatingFileHandler(
                f"{log_dir}/webhook-app.log",
                maxBytes=10*1024*1024,  # 10MB
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )

setup_logging()
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Security headers
@app.after_request
def add_security_headers(response):
    """Thêm security headers"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    if os.environ.get('USE_HTTPS', 'false').lower() == 'true':
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response

# Enable CORS for all routes
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Khởi tạo AWS translator
translator = AWSTranslator()

class EmailProcessor:
    """Class để xử lý dữ liệu email từ Cloudflare webhook"""
    
    def __init__(self):
        self.processed_emails = []
        self.max_emails = 1000  # Giới hạn số email lưu trữ
    
    def process_email(self, email_data):
        """Xử lý dữ liệu email nhận được"""
        try:
            # Tạo timestamp
            timestamp = datetime.now().isoformat()
            
            # Validate email data
            if not email_data.get("from") or not email_data.get("to"):
                logger.warning("Email data thiếu thông tin from/to")
                return {"error": "Missing required fields: from, to"}
            
            # Translate subject nếu có
            original_subject = email_data.get("subject", "")
            translation_info = translator.translate_subject(original_subject)
            
            # Tạo object email đã xử lý
            processed_email = {
                "timestamp": timestamp,
                "from": email_data.get("from", ""),
                "to": email_data.get("to", ""),
                "subject": {
                    "original": translation_info["original"],
                    "translated": translation_info["translated"],
                    "language_detected": translation_info["language_detected"],
                    "translation_status": translation_info["translation_status"]
                },
                "body": email_data.get("body", ""),
                "status": "processed"
            }
            
            # Thêm vào danh sách đã xử lý (với giới hạn)
            self.processed_emails.append(processed_email)
            if len(self.processed_emails) > self.max_emails:
                self.processed_emails.pop(0)  # Xóa email cũ nhất
            
            # Log thông tin email (không log body để bảo mật)
            logger.info(f"Email processed: From={processed_email['from']}, To={processed_email['to']}, Subject={translation_info['original']} -> {translation_info['translated']}")
            
            return processed_email
            
        except Exception as e:
            logger.error(f"Error processing email: {str(e)}")
            return {"error": str(e)}

# Khởi tạo email processor
email_processor = EmailProcessor()

@app.route('/')
def home():
    """Trang chủ"""
    return jsonify({
        "message": "Cloudflare Webhook Email Receiver with OpenAI Translation",
        "status": "running",
        "version": "1.0.0",
        "environment": os.environ.get('FLASK_ENV', 'production'),
        "https_enabled": os.environ.get('USE_HTTPS', 'false').lower() == 'true',
        "translation_enabled": translator.enabled,
        "endpoints": {
            "receive_email": "/api/email",
            "get_emails": "/api/emails",
            "health": "/health",
            "metrics": "/metrics",
            "translate": "/api/translate"
        }
    })

@app.route('/api/email', methods=['POST', 'OPTIONS'])
def receive_email():
    """Endpoint để nhận email từ Cloudflare webhook"""
    if request.method == 'OPTIONS':
        # Handle preflight request
        response = jsonify({"message": "OK"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        return response, 200
    
    try:
        # Log request details
        logger.info(f"Received {request.method} request to /api/email")
        logger.info(f"Headers: {dict(request.headers)}")
        
        # Lấy dữ liệu JSON từ request
        email_data = request.get_json()
        
        if not email_data:
            logger.warning("No JSON data received")
            return jsonify({"error": "No JSON data received"}), 400
        
        # Lấy và translate subject trực tiếp trong function này
        original_subject = email_data.get("subject", "")
        logger.info(f"Original subject: '{original_subject}'")
        
        # Translate subject sử dụng OpenAI
        translation_info = translator.translate_subject(original_subject)
        logger.info(f"Translation result: {translation_info}")
        
        # Cập nhật email_data với thông tin translation
        email_data["subject_translation"] = translation_info
        
        # Log dữ liệu nhận được (không log body để bảo mật)
        safe_data = {k: v for k, v in email_data.items() if k not in ['body', 'subject_translation']}
        logger.info(f"Received email data: {json.dumps(safe_data, indent=2)}")
        logger.info(f"Subject translation: {json.dumps(translation_info, indent=2)}")
        
        # Xử lý email
        processed_email = email_processor.process_email(email_data)
        
        if "error" in processed_email:
            return jsonify({"error": processed_email["error"]}), 400
        
        # Trả về response thành công với thông tin translation
        response = jsonify({
            "message": "Email received successfully",
            "email": processed_email,
            "translation_info": {
                "original_subject": original_subject,
                "translated_subject": translation_info["translated"],
                "language_detected": translation_info["language_detected"],
                "translation_status": translation_info["translation_status"]
            }
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
        
    except Exception as e:
        logger.error(f"Error in receive_email endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Endpoint để lấy danh sách email đã xử lý"""
    try:
        return jsonify({
            "emails": email_processor.processed_emails,
            "count": len(email_processor.processed_emails),
            "total_count": len(email_processor.processed_emails)
        }), 200
    except Exception as e:
        logger.error(f"Error in get_emails endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/translate', methods=['POST'])
def translate_text():
    """Endpoint để translate text"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "Text field is required"}), 400
        
        text = data['text']
        translation_info = translator.translate_subject(text)
        
        return jsonify({
            "translation": translation_info,
            "translator_enabled": translator.enabled
        }), 200
        
    except Exception as e:
        logger.error(f"Error in translate endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "processed_emails_count": len(email_processor.processed_emails),
        "translation_enabled": translator.enabled,
        "uptime": "running"
    }), 200

@app.route('/metrics', methods=['GET'])
def metrics():
    """Metrics endpoint"""
    return jsonify({
        "total_emails_processed": len(email_processor.processed_emails),
        "max_emails_stored": email_processor.max_emails,
        "current_storage_usage": f"{(len(email_processor.processed_emails) / email_processor.max_emails) * 100:.1f}%",
        "translation_enabled": translator.enabled,
        "timestamp": datetime.now().isoformat()
    }), 200

@app.errorhandler(403)
def forbidden(error):
    logger.error(f"403 Forbidden error: {error}")
    return jsonify({
        "error": "Forbidden",
        "message": "Access denied. Check your request headers and CORS settings.",
        "status_code": 403
    }), 403

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"500 Internal Server Error: {error}")
    return jsonify({"error": "Internal server error"}), 500

def get_ssl_context():
    """Lấy SSL context nếu HTTPS được bật"""
    if os.environ.get('USE_HTTPS', 'false').lower() == 'true':
        cert_path = os.environ.get('SSL_CERT_PATH', 'ssl/cert.pem')
        key_path = os.environ.get('SSL_KEY_PATH', 'ssl/key.pem')
        
        if os.path.exists(cert_path) and os.path.exists(key_path):
            return cert_path, key_path
        else:
            logger.warning("SSL certificate không tìm thấy. Chạy 'python ssl_config.py' để tạo certificate.")
            return None, None
    return None, None

if __name__ == '__main__':
    # Lấy cấu hình từ environment
    port = int(os.environ.get('PORT', 5000))
    use_https = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info("🚀 Khởi động Webhook Server với AWS Translation...")
    logger.info(f"Environment: {os.environ.get('FLASK_ENV', 'production')}")
    logger.info(f"Port: {port}")
    logger.info(f"HTTPS: {use_https}")
    logger.info(f"Translation: {'Enabled' if translator.enabled else 'Disabled'}")
    
    if use_https:
        cert_path, key_path = get_ssl_context()
        if cert_path and key_path:
            logger.info(f"🔒 Khởi động HTTPS server tại https://0.0.0.0:{port}")
            app.run(
                host='0.0.0.0',
                port=port,
                debug=debug_mode,
                ssl_context=(cert_path, key_path)
            )
        else:
            logger.error("❌ Không thể khởi động HTTPS server. Certificate không tìm thấy.")
            logger.info("💡 Chạy 'python ssl_config.py' để tạo SSL certificate")
    else:
        logger.info(f"🌐 Khởi động HTTP server tại http://0.0.0.0:{port}")
        app.run(
            host='0.0.0.0',
            port=port,
            debug=debug_mode
        ) 