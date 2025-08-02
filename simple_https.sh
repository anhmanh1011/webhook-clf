#!/bin/bash

echo "🔐 Setup HTTPS đơn giản với Flask SSL..."

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

# Tạo SSL certificate
echo "🔐 Tạo SSL certificate..."
python3 ssl_config.py

# Cấu hình HTTPS
echo "⚙️ Cấu hình HTTPS..."
cat > .env << 'ENV_EOF'
PORT=5000
FLASK_ENV=production
LOG_LEVEL=INFO
USE_HTTPS=true
SSL_CERT_PATH=ssl/cert.pem
SSL_KEY_PATH=ssl/key.pem
ENV_EOF

echo "✅ HTTPS setup hoàn tất!"
echo "🚀 Khởi động server HTTPS..."
echo "🌐 Truy cập: https://138.89.142.88:5000"
echo "🔧 Test: curl -k https://138.89.142.88:5000/health"

# Chạy app
python3 app.py 