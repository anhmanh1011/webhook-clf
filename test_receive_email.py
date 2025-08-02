#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

def test_receive_email_translation():
    """Test function receive_email với translation"""
    
    # Cấu hình
    server_domain = "api.lewistechnicalsolutions.com"
    port = 5000
    
    print("🧪 Testing receive_email function với translation...")
    print("=" * 60)
    
    # Test cases với các ngôn ngữ khác nhau
    test_cases = [
        {
            "name": "Vietnamese Subject",
            "subject": "Thông báo quan trọng về dự án mới",
            "expected_lang": "vi"
        },
        {
            "name": "English Subject",
            "subject": "Important notification about new project",
            "expected_lang": "en"
        },
        {
            "name": "French Subject",
            "subject": "Notification importante sur le nouveau projet",
            "expected_lang": "fr"
        },
        {
            "name": "Empty Subject",
            "subject": "",
            "expected_lang": "unknown"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{i}. Testing: {test_case['name']}")
        print("-" * 40)
        
        try:
            email_data = {
                "from": f"test{i}@example.com",
                "to": "user@example.com",
                "subject": test_case["subject"],
                "body": f"This is test email {i} with {test_case['name']}"
            }
            
            print(f"Original subject: '{test_case['subject']}'")
            
            response = requests.post(
                f"https://{server_domain}:{port}/api/email",
                headers={"Content-Type": "application/json"},
                json=email_data,
                verify=True,
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Email sent successfully!")
                result = response.json()
                
                # Kiểm tra translation_info trong response
                if "translation_info" in result:
                    translation = result["translation_info"]
                    print(f"Original subject: {translation['original_subject']}")
                    print(f"Translated subject: {translation['translated_subject']}")
                    print(f"Language detected: {translation['language_detected']}")
                    print(f"Translation status: {translation['translation_status']}")
                    
                    # Kiểm tra email object
                    if "email" in result and "subject" in result["email"]:
                        email_subject = result["email"]["subject"]
                        print(f"Email subject original: {email_subject['original']}")
                        print(f"Email subject translated: {email_subject['translated']}")
                else:
                    print("⚠️ No translation_info in response")
                    print(f"Response: {json.dumps(result, indent=2)}")
                    
            else:
                print(f"❌ Email failed. Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 60)
    
    # Test get all emails để xem kết quả
    print("📧 Getting all emails to verify translation...")
    try:
        response = requests.get(
            f"https://{server_domain}:{port}/api/emails",
            verify=True,
            timeout=10
        )
        
        if response.status_code == 200:
            emails = response.json()
            print(f"Total emails: {emails.get('count', 0)}")
            
            # Hiển thị 3 email cuối cùng
            for i, email in enumerate(emails.get('emails', [])[-3:], 1):
                print(f"\nEmail {i}:")
                print(f"  From: {email['from']}")
                print(f"  To: {email['to']}")
                print(f"  Original Subject: {email['subject']['original']}")
                print(f"  Translated Subject: {email['subject']['translated']}")
                print(f"  Language: {email['subject']['language_detected']}")
                print(f"  Status: {email['subject']['translation_status']}")
        else:
            print(f"❌ Failed to get emails. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error getting emails: {e}")

if __name__ == "__main__":
    test_receive_email_translation() 