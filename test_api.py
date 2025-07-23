#!/usr/bin/env python3
"""
Test script to verify that the SIEM Lite API works correctly.
"""

import requests
import json
import time
import sys

def test_api():
    """Test the main API routes."""
    base_url = "http://127.0.0.1:8000"
    
    print("🧪 Testing SIEM Lite API...")
    print(f"🔗 Base URL: {base_url}")
    
    # Wait a bit for the server to be ready
    time.sleep(2)
    
    try:
        # 1. Test health check
        print("\n📡 1. Testing /api/health...")
        response = requests.get(f"{base_url}/api/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Status: {data.get('status', 'unknown')}")
            print(f"   🗄️ Database: {data.get('database', 'unknown')}")
            print(f"   🕐 Timestamp: {data.get('timestamp', 'unknown')}")
        else:
            print(f"   ❌ Error: {response.text}")
            
        # 2. Test detailed health check
        print("\n📡 2. Testing /api/health?detailed=true...")
        response = requests.get(f"{base_url}/api/health?detailed=true", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Detailed status available")
            if "details" in data:
                print(f"   📊 Total alerts: {data['details'].get('total_alerts', 0)}")
        
        # 3. Test main page
        print("\n📡 3. Testing / (main page)...")
        response = requests.get(f"{base_url}/", timeout=10)
        print(f"   Status: {response.status_code}")
        
        # 4. Test documentation
        print("\n📡 4. Testing /docs (documentation)...")
        response = requests.get(f"{base_url}/docs", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Swagger documentation available")
        
        # 5. Test alerts list
        print("\n📡 5. Testing /api/alerts...")
        response = requests.get(f"{base_url}/api/alerts", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            alerts = response.json()
            print(f"   ✅ {len(alerts)} alerts found")
        
        # 6. Create a test alert
        print("\n📡 6. Creating test alert...")
        test_alert = {
            "alert_type": "Test Alert",
            "source_ip": "192.168.1.100", 
            "details": "Automatically created test alert"
        }
        response = requests.post(
            f"{base_url}/api/alerts",
            json=test_alert,
            timeout=10,
            headers={"Content-Type": "application/json"}
        )
        print(f"   Status: {response.status_code}")
        if response.status_code in [200, 201]:
            alert_data = response.json()
            print(f"   ✅ Alert created with ID: {alert_data.get('id', 'unknown')}")
        else:
            print(f"   ❌ Error creating alert: {response.text}")
        
        # 7. Test metrics
        print("\n📡 7. Testing /api/metrics...")
        response = requests.get(f"{base_url}/api/metrics", timeout=10)
        print(f"   Status: {response.status_code}")
        
        print("\n🎉 All tests completed!")
        print("\n🔗 Important URLs:")
        print(f"   📚 Documentation: {base_url}/docs")
        print(f"   ❤️ Health Check: {base_url}/api/health")
        print(f"   🚨 Alerts: {base_url}/api/alerts")
        print(f"   📊 Metrics: {base_url}/api/metrics")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Cannot connect to server.")
        print("   Make sure the server is running on http://127.0.0.1:8000")
        print("   Command: uvicorn siem_lite.main:app --host 127.0.0.1 --port 8000")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    test_api()
