#!/bin/bash

echo "🤖 Setup Webhook App với OpenAI Translation..."

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 không được tìm thấy"
    exit 1
fi

# Tạo virtual environment nếu chưa có
if [ ! -d "venv" ]; then
    echo "🐍 Tạo virtual environment..."
    python3 -m venv venv
fi

# Kích hoạt virtual environment
echo "⚡ Kích hoạt virtual environment..."
source venv/bin/activate

# Cài đặt dependencies
echo "📦 Cài đặt dependencies..."
pip install -r requirements.txt

# Tạo file .env
echo "⚙️ Tạo file .env..."
cat > .env << 'ENV_EOF'
PORT=5000
FLASK_ENV=production
LOG_LEVEL=INFO
USE_HTTPS=true
SSL_CERT_PATH=/etc/letsencrypt/live/api.lewistechnicalsolutions.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/api.lewistechnicalsolutions.com/privkey.pem
OPENAI_API_KEY=your_openai_api_key_here
ENV_EOF

echo "✅ Setup hoàn tất!"
echo "🔑 Hãy cập nhật OPENAI_API_KEY trong file .env"
echo "🚀 Khởi động server: bash run_https.sh"
echo "🧪 Test translation: python test_translation.py" 