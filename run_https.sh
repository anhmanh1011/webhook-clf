#!/bin/bash

echo "🚀 Khởi động HTTPS server với Let's Encrypt certificate..."

# Kích hoạt virtual environment
source venv/bin/activate

# Cấu hình HTTPS với Let's Encrypt
echo "⚙️ Cấu hình HTTPS với Let's Encrypt..."
cat > .env << 'ENV_EOF'
PORT=5000
FLASK_ENV=production
USE_HTTPS=true
SSL_CERT_PATH=/etc/letsencrypt/live/api.lewistechnicalsolutions.com/fullchain.pem
SSL_KEY_PATH=/etc/letsencrypt/live/api.lewistechnicalsolutions.com/privkey.pem
ENV_EOF

# Kiểm tra certificate
echo "🔐 Kiểm tra Let's Encrypt certificate..."
if [ -f "/etc/letsencrypt/live/api.lewistechnicalsolutions.com/fullchain.pem" ] && [ -f "/etc/letsencrypt/live/api.lewistechnicalsolutions.com/privkey.pem" ]; then
    echo "✅ Let's Encrypt certificate found!"
else
    echo "❌ Let's Encrypt certificate not found!"
    echo "💡 Please run: sudo certbot certonly --standalone -d api.lewistechnicalsolutions.com"
    exit 1
fi

echo "✅ HTTPS server sẵn sàng!"
echo "🌐 Truy cập: https://api.lewistechnicalsolutions.com:5000"
echo "🔧 Test: curl https://api.lewistechnicalsolutions.com:5000/health"

# Chạy app
python3 app.py 