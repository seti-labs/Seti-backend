#!/bin/bash
# Test script for Markets API

echo "🧪 Testing Markets API"
echo "===================="
echo ""

# Test 1: Basic markets endpoint
echo "1️⃣ Testing basic markets endpoint..."
response=$(curl -s 'http://localhost:5001/api/v1/markets?page=1&per_page=5')

if [ -z "$response" ]; then
    echo "❌ No response - Backend may not be running"
    echo "   Start backend with: python3 run.py"
    exit 1
fi

# Test 2: Parse JSON response
echo "$response" | python3 << 'PYTHON'
import sys, json
try:
    data = json.load(sys.stdin)
    markets = data.get('markets', [])
    pagination = data.get('pagination', {})
    
    print(f"✅ API Response Received!")
    print(f"")
    print(f"📊 Statistics:")
    print(f"   Markets in this page: {len(markets)}")
    print(f"   Total markets: {pagination.get('total', 0)}")
    print(f"   Page: {pagination.get('page', 1)} of {pagination.get('pages', 1)}")
    print(f"")
    
    if markets:
        print(f"📋 Sample Markets:")
        for i, market in enumerate(markets[:5], 1):
            question = market.get('question', 'Unknown')[:70]
            category = market.get('category', 'N/A')
            resolved = "✅ Resolved" if market.get('resolved') else "⏳ Active"
            print(f"   {i}. [{category}] {resolved}")
            print(f"      {question}...")
        print(f"")
        print(f"✅ Markets are being fetched successfully!")
    else:
        print(f"⚠️  No markets found")
        print(f"   This may trigger auto-sync from Polymarket on next request")
        
except json.JSONDecodeError as e:
    print(f"❌ Invalid JSON response: {e}")
    print(f"   Response: {sys.stdin.read()[:200]}")
except Exception as e:
    print(f"❌ Error: {e}")
PYTHON

echo ""
echo "2️⃣ Testing with filters..."
echo ""

# Test with status filter
echo "   Active markets only:"
curl -s 'http://localhost:5001/api/v1/markets?page=1&per_page=3&status=active' | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'   ✅ Found {len(data.get(\"markets\", []))} active markets')" 2>&1

echo ""
echo "3️⃣ Testing auto-sync (checking for new markets)..."
echo "   Making request to trigger auto-sync..."
curl -s 'http://localhost:5001/api/v1/markets?page=1&per_page=1' > /dev/null
echo "   ✅ Request sent - check backend terminal for auto-sync messages"
echo ""

echo "✅ All tests complete!"
echo ""
echo "📝 Next steps:"
echo "   - Check backend logs for '✅ Auto-synced X markets from Polymarket'"
echo "   - Markets will auto-refresh every 10 seconds in frontend"
echo "   - Open http://localhost:5173 to see markets in UI"

