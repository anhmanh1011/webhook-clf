#!/bin/bash

echo "🚀 Khởi động HTTP server..."

# Kích hoạt virtual environment
source venv/bin/activate

# Cấu hình HTTP
echo "⚙️ Cấu hình HTTP..."
cat > .env << 'ENV_EOF'
PORT=5000
FLASK_ENV=production
USE_HTTPS=false
ENV_EOF

echo "✅ HTTP server sẵn sàng!"
echo "🌐 Truy cập: http://138.89.142.88:5000"
echo "🔧 Test: curl http://138.89.142.88:5000/health"

# Chạy app
python3 app.py 