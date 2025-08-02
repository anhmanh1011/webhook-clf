#!/bin/bash

echo "🚀 Khởi động HTTPS server..."

# Kích hoạt virtual environment
source venv/bin/activate

# Kiểm tra SSL certificate
if [ ! -f "ssl/cert.pem" ] || [ ! -f "ssl/key.pem" ]; then
    echo "🔐 Tạo SSL certificate..."
    python3 ssl_config.py
fi

# Cấu hình HTTPS
echo "⚙️ Cấu hình HTTPS..."
cat > .env << 'ENV_EOF'
PORT=5000
FLASK_ENV=production
USE_HTTPS=true
SSL_CERT_PATH=ssl/cert.pem
SSL_KEY_PATH=ssl/key.pem
ENV_EOF

echo "✅ HTTPS server sẵn sàng!"
echo "🌐 Truy cập: https://138.89.142.88:5000"
echo "🔧 Test: curl -k https://138.89.142.88:5000/health"

# Chạy app
python3 app.py 