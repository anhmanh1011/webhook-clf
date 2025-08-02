#!/bin/bash

echo "🧪 Testing HTTPS webhook với Let's Encrypt certificate..."

SERVER_DOMAIN="api.lewistechnicalsolutions.com"
PORT="5000"

echo "🌐 Server: https://$SERVER_DOMAIN:$PORT"
echo "=================================================="

# Test 1: Health check
echo "1. Testing health check:"
curl -s https://$SERVER_DOMAIN:$PORT/health | jq .
echo -e "\n"

# Test 2: Send email
echo "2. Testing send email:"
curl -X POST https://$SERVER_DOMAIN:$PORT/api/email \
  -H "Content-Type: application/json" \
  -d '{
    "from": "test@example.com",
    "to": "user@example.com",
    "subject": "Test Let'\''s Encrypt Email",
    "body": "Testing HTTPS webhook with Let'\''s Encrypt certificate"
  }' | jq .
echo -e "\n"

# Test 3: Get emails
echo "3. Testing get emails:"
curl -s https://$SERVER_DOMAIN:$PORT/api/emails | jq .
echo -e "\n"

# Test 4: Metrics
echo "4. Testing metrics:"
curl -s https://$SERVER_DOMAIN:$PORT/metrics | jq .
echo -e "\n"

echo "✅ Testing completed!" 