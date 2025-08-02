#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

def test_webhook():
    """Test webhook với HTTPS và Let's Encrypt certificate"""
    
    # Cấu hình
    use_https = os.environ.get('USE_HTTPS', 'false').lower() == 'true'
    protocol = "https" if use_https else "http"
    server_domain = "api.lewistechnicalsolutions.com"
    port = 5000
    
    webhook_url = f"{protocol}://{server_domain}:{port}/api/email"
    
    print("🧪 Testing Cloudflare Webhook với Let's Encrypt HTTPS...")
    print("=" * 50)
    
    # Test 1: Send email webhook
    print("1. Testing send email webhook:")
    try:
        email_data = {
            "from": "test@example.com",
            "to": "user@example.com",
            "subject": f"Test Email {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "body": "This is a test email from Cloudflare webhook with Let's Encrypt"
        }
        
        # Sử dụng verify=True vì có certificate thật
        response = requests.post(
            webhook_url,
            headers={"Content-Type": "application/json"},
            json=email_data,
            verify=True,  # Sử dụng certificate thật
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Email sent successfully!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Failed to send email. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.SSLError as e:
        print(f"❌ SSL Error: {e}")
        print("💡 Kiểm tra certificate có hợp lệ không")
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: {e}")
        print("💡 Kiểm tra server có đang chạy không")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Get emails
    print("2. Testing get emails:")
    try:
        get_url = f"{protocol}://{server_domain}:{port}/api/emails"
        response = requests.get(get_url, verify=True, timeout=10)
        
        if response.status_code == 200:
            print("✅ Retrieved emails successfully!")
            emails = response.json()
            print(f"Total emails: {emails.get('count', 0)}")
            if emails.get('emails'):
                print("Latest email:")
                print(json.dumps(emails['emails'][-1], indent=2))
        else:
            print(f"❌ Failed to get emails. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Health check
    print("3. Testing health check:")
    try:
        health_url = f"{protocol}://{server_domain}:{port}/health"
        response = requests.get(health_url, verify=True, timeout=10)
        
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"Response: {response.json()}")
        else:
            print(f"❌ Health check failed. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_webhook() 