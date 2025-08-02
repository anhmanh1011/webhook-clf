# Cloudflare Webhook Email Receiver

Project Python đơn giản để nhận và xử lý dữ liệu email từ Cloudflare webhook.

## Tính năng

- ✅ Nhận dữ liệu email từ Cloudflare webhook
- ✅ Xử lý và lưu trữ thông tin email (from, to, subject, body)
- ✅ API endpoints để quản lý email
- ✅ Health check endpoint
- ✅ Logging chi tiết
- ✅ Error handling

## Cài đặt

1. **Clone repository:**
```bash
git clone <repository-url>
cd webhook-clf
```

2. **Cài đặt dependencies:**
```bash
pip install -r requirements.txt
```

3. **Chạy ứng dụng:**
```bash
python app.py
```

Server sẽ chạy tại `http://localhost:5000`

## API Endpoints

### 1. Trang chủ
- **URL:** `GET /`
- **Mô tả:** Hiển thị thông tin về API

### 2. Nhận email webhook
- **URL:** `POST /api/email`
- **Mô tả:** Endpoint để nhận dữ liệu email từ Cloudflare
- **Body:** JSON với cấu trúc:
```json
{
  "from": "sender@example.com",
  "to": "recipient@example.com",
  "subject": "Email Subject",
  "body": "Email content"
}
```

### 3. Lấy danh sách email
- **URL:** `GET /api/emails`
- **Mô tả:** Lấy tất cả email đã xử lý

### 4. Health check
- **URL:** `GET /health`
- **Mô tả:** Kiểm tra trạng thái server

## Cấu hình Cloudflare

Để sử dụng với Cloudflare, cấu hình webhook trong Cloudflare Workers như sau:

```javascript
export default {
  async email(message) {
    const from = message.from;
    const to = message.recipients.join(", ");
    const subject = message.headers.get("subject") || "";
    const body = await new Response(message.raw).text();

    await fetch("https://your-webhook.com/api/email", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        from,
        to,
        subject,
        body
      })
    });
  }
}
```

## Testing

Chạy test để kiểm tra webhook:

```bash
python test_webhook.py
```

## Environment Variables

Tạo file `.env` để cấu hình:

```env
PORT=5000
FLASK_ENV=development
```

## Cấu trúc Project

```
webhook-clf/
├── app.py              # Flask application chính
├── test_webhook.py     # Test script
├── requirements.txt    # Python dependencies
├── README.md          # Documentation
└── .env               # Environment variables (tạo thủ công)
```

## Deployment

### Local Development
```bash
python app.py
```

### Production (với Gunicorn)
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Docker
```bash
docker build -t webhook-clf .
docker run -p 5000:5000 webhook-clf
```

## Logs

Ứng dụng sẽ log các thông tin sau:
- Email nhận được
- Lỗi xử lý
- Health check status

## Troubleshooting

1. **Port đã được sử dụng:** Thay đổi PORT trong file `.env`
2. **Không nhận được webhook:** Kiểm tra URL và firewall
3. **Lỗi JSON:** Đảm bảo dữ liệu gửi đúng format

## License

MIT License 