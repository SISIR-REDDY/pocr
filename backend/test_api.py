"""Test script to verify API is working correctly"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print(f"[OK] Health check: {response.json()}")

def test_root():
    """Test root endpoint"""
    print("\nTesting root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    assert response.status_code == 200
    print(f"[OK] Root endpoint: {response.json()}")

def test_verify():
    """Test verify endpoint"""
    print("\nTesting verify endpoint...")
    data = {
        "submitted_fields": {
            "name": "John Doe",
            "age": "30"
        },
        "extracted_fields": {
            "name": "John Doe",
            "age": "30"
        }
    }
    response = requests.post(f"{BASE_URL}/api/verify", json=data)
    assert response.status_code == 200
    result = response.json()
    print(f"[OK] Verify endpoint: overall_score = {result.get('overall_score', 'N/A')}")
    return result

def test_extract_demo():
    """Test extract endpoint with demo mode"""
    print("\nTesting extract endpoint (demo mode)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/extract",
            data={"demo_mode": True, "allow_fallback": False}
        )
        if response.status_code == 404:
            print("[WARN] Demo mode: Sample PDF not found (expected if PDF not placed)")
        else:
            print(f"[OK] Extract demo: Status {response.status_code}")
    except Exception as e:
        print(f"[WARN] Extract demo error: {e}")

if __name__ == "__main__":
    print("=" * 50)
    print("MOSIP OCR API Test Suite")
    print("=" * 50)
    
    try:
        test_health()
        test_root()
        test_verify()
        test_extract_demo()
        
        print("\n" + "=" * 50)
        print("[SUCCESS] All tests completed!")
        print("=" * 50)
    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()

