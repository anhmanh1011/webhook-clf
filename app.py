from flask import Flask, request, jsonify
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

class EmailProcessor:
    """Class để xử lý dữ liệu email từ Cloudflare webhook"""
    
    def __init__(self):
        self.processed_emails = []
    
    def process_email(self, email_data):
        """Xử lý dữ liệu email nhận được"""
        try:
            # Tạo timestamp
            timestamp = datetime.now().isoformat()
            
            # Tạo object email đã xử lý
            processed_email = {
                "timestamp": timestamp,
                "from": email_data.get("from", ""),
                "to": email_data.get("to", ""),
                "subject": email_data.get("subject", ""),
                "body": email_data.get("body", ""),
                "status": "processed"
            }
            
            # Thêm vào danh sách đã xử lý
            self.processed_emails.append(processed_email)
            
            # Log thông tin email
            logger.info(f"Email processed: From={processed_email['from']}, To={processed_email['to']}, Subject={processed_email['subject']}")
            
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
        "message": "Cloudflare Webhook Email Receiver",
        "status": "running",
        "endpoints": {
            "receive_email": "/api/email",
            "get_emails": "/api/emails",
            "health": "/health"
        }
    })

@app.route('/api/email', methods=['POST'])
def receive_email():
    """Endpoint để nhận email từ Cloudflare webhook"""
    try:
        # Kiểm tra method
        if request.method != 'POST':
            return jsonify({"error": "Method not allowed"}), 405
        
        # Lấy dữ liệu JSON từ request
        email_data = request.get_json()
        
        if not email_data:
            return jsonify({"error": "No JSON data received"}), 400
        
        # Log dữ liệu nhận được
        logger.info(f"Received email data: {json.dumps(email_data, indent=2)}")
        
        # Xử lý email
        processed_email = email_processor.process_email(email_data)
        
        # Trả về response thành công
        return jsonify({
            "message": "Email received successfully",
            "email": processed_email
        }), 200
        
    except Exception as e:
        logger.error(f"Error in receive_email endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Endpoint để lấy danh sách email đã xử lý"""
    try:
        return jsonify({
            "emails": email_processor.processed_emails,
            "count": len(email_processor.processed_emails)
        }), 200
    except Exception as e:
        logger.error(f"Error in get_emails endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "processed_emails_count": len(email_processor.processed_emails)
    }), 200

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    # Lấy port từ environment variable hoặc sử dụng default
    port = int(os.environ.get('PORT', 5000))
    
    # Chạy app
    app.run(
        host='0.0.0.0',
        port=port,
        debug=os.environ.get('FLASK_ENV') == 'development'
    ) 