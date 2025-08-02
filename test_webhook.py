import requests
import json

def test_webhook():
    """Test function để gửi dữ liệu email mẫu đến webhook"""
    
    # URL của webhook (thay đổi theo địa chỉ server của bạn)
    webhook_url = "http://38.89.142.88:5000/api/email"
    
    # Dữ liệu email mẫu theo cấu trúc Cloudflare
    sample_email_data = {
        "from": "sender@example.com",
        "to": "recipient1@example.com, recipient2@example.com",
        "subject": "Test Email Subject",
        "body": "This is a test email body content.\n\nBest regards,\nTest Sender"
    }
    
    try:
        # Gửi POST request đến webhook
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            data=json.dumps(sample_email_data)
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
        if response.status_code == 200:
            print("✅ Webhook test thành công!")
        else:
            print("❌ Webhook test thất bại!")
            
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến server. Hãy đảm bảo server đang chạy.")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

def test_get_emails():
    """Test function để lấy danh sách email đã xử lý"""
    
    webhook_url = "http://38.89.142.88:5000/api/emails"
    
    try:
        response = requests.get(webhook_url)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Không thể kết nối đến server.")
    except Exception as e:
        print(f"❌ Lỗi: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing Cloudflare Webhook...")
    print("=" * 50)
    
    # Test gửi email
    print("1. Testing send email webhook:")
    test_webhook()
    
    print("\n" + "=" * 50)
    
    # Test lấy danh sách email
    print("2. Testing get emails:")
    test_get_emails() 