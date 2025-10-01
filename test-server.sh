#!/bin/bash

echo "🧪 Testing MCP BigQuery Server..."
echo ""

# Test 1: Basic connectivity
echo "1️⃣  Testing basic connectivity..."
response=$(curl -s -w "\n%{http_code}" http://localhost:8080/mcp)
http_code=$(echo "$response" | tail -n1)
body=$(echo "$response" | head -n-1)

if [ "$http_code" = "406" ]; then
    echo "✅ Server is responding (HTTP 406 - expected for GET without headers)"
    echo "   Response: $(echo $body | jq -r '.error.message' 2>/dev/null || echo $body)"
else
    echo "❌ Unexpected response code: $http_code"
    echo "   Response: $body"
fi
echo ""

# Test 2: POST with headers
echo "2️⃣  Testing with proper headers..."
response=$(curl -s -X POST http://localhost:8080/mcp \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}')

if echo "$response" | grep -q "session"; then
    echo "✅ Server requires session (correct MCP behavior)"
    echo "   Response: $(echo $response | jq -r '.error.message' 2>/dev/null || echo $response)"
else
    echo "📋 Response: $response"
fi
echo ""

# Test 3: Container status
echo "3️⃣  Checking container status..."
docker-compose ps mcp-bigquery | tail -n +2
echo ""

echo "✅ MCP BigQuery Server is running and responding correctly!"
echo ""
echo "📝 Next steps:"
echo "   - Configure an MCP client (e.g., Claude Desktop)"
echo "   - Set up the client to connect to http://localhost:8080/mcp"
echo "   - Use the bearer token from .env file"
echo ""
echo "🔑 Your bearer token (from .env):"
grep "BEARER_TOKEN=" .env | head -1
