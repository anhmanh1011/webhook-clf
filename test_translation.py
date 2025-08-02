#!/usr/bin/env python3
import requests
import json
import os
from datetime import datetime

def test_translation():
    """Test translation functionality"""
    
    # Cấu hình
    server_domain = "api.lewistechnicalsolutions.com"
    port = 5000
    
    print("🧪 Testing OpenAI Translation...")
    print("=" * 50)
    
    # Test 1: Translate endpoint
    print("1. Testing translate endpoint:")
    try:
        translate_data = {
            "text": "Xin chào, đây là email test bằng tiếng Việt"
        }
        
        response = requests.post(
            f"https://{server_domain}:{port}/api/translate",
            headers={"Content-Type": "application/json"},
            json=translate_data,
            verify=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Translation successful!")
            result = response.json()
            print(f"Original: {result['translation']['original']}")
            print(f"Translated: {result['translation']['translated']}")
            print(f"Language: {result['translation']['language_detected']}")
            print(f"Status: {result['translation']['translation_status']}")
        else:
            print(f"❌ Translation failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 2: Email with Vietnamese subject
    print("2. Testing email with Vietnamese subject:")
    try:
        email_data = {
            "from": "test@example.com",
            "to": "user@example.com",
            "subject": "Thông báo quan trọng về dự án mới",
            "body": "Đây là nội dung email bằng tiếng Việt"
        }
        
        response = requests.post(
            f"https://{server_domain}:{port}/api/email",
            headers={"Content-Type": "application/json"},
            json=email_data,
            verify=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Email with translation sent successfully!")
            result = response.json()
            subject_info = result['email']['subject']
            print(f"Original subject: {subject_info['original']}")
            print(f"Translated subject: {subject_info['translated']}")
            print(f"Language detected: {subject_info['language_detected']}")
        else:
            print(f"❌ Email failed. Status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 3: Email with English subject
    print("3. Testing email with English subject:")
    try:
        email_data = {
            "from": "test@example.com",
            "to": "user@example.com",
            "subject": "Important notification about new project",
            "body": "This is email content in English"
        }
        
        response = requests.post(
            f"https://{server_domain}:{port}/api/email",
            headers={"Content-Type": "application/json"},
            json=email_data,
            verify=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Email with English subject sent successfully!")
            result = response.json()
            subject_info = result['email']['subject']
            print(f"Original subject: {subject_info['original']}")
            print(f"Translated subject: {subject_info['translated']}")
            print(f"Language detected: {subject_info['language_detected']}")
        else:
            print(f"❌ Email failed. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    
    # Test 4: Get all emails
    print("4. Testing get all emails:")
    try:
        response = requests.get(
            f"https://{server_domain}:{port}/api/emails",
            verify=True,
            timeout=10
        )
        
        if response.status_code == 200:
            print("✅ Retrieved emails successfully!")
            emails = response.json()
            print(f"Total emails: {emails.get('count', 0)}")
            
            for i, email in enumerate(emails.get('emails', [])[-3:], 1):  # Show last 3 emails
                print(f"\nEmail {i}:")
                print(f"  From: {email['from']}")
                print(f"  To: {email['to']}")
                print(f"  Original Subject: {email['subject']['original']}")
                print(f"  Translated Subject: {email['subject']['translated']}")
                print(f"  Language: {email['subject']['language_detected']}")
        else:
            print(f"❌ Failed to get emails. Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_translation() 