"""
Test script to verify API functionality without running the Discord bot.
This tests the API routes directly using FastAPI's test client.
"""

from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.app import app

client = TestClient(app)


def test_root():
    """Test root endpoint"""
    print("Testing root endpoint...")
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "Discord Bot API"
    print("✓ Root endpoint works")


def test_health():
    """Test health check endpoint (no auth required)"""
    print("\nTesting health check endpoint...")
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    print("✓ Health check works")


def test_status_without_auth():
    """Test status endpoint without authentication (should fail)"""
    print("\nTesting status endpoint without auth...")
    response = client.get("/api/status")
    assert response.status_code == 401
    print("✓ Status endpoint requires authentication")


def test_status_with_auth():
    """Test status endpoint with authentication"""
    print("\nTesting status endpoint with auth...")
    headers = {"X-API-Key": "test_api_key_12345"}
    response = client.get("/api/status", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    print("✓ Status endpoint works with authentication")


def test_clans_without_auth():
    """Test clans endpoint without authentication (should fail)"""
    print("\nTesting clans endpoint without auth...")
    response = client.get("/api/clans/")
    assert response.status_code == 401
    print("✓ Clans endpoint requires authentication")


def test_clans_with_auth():
    """Test clans endpoint with authentication"""
    print("\nTesting clans endpoint with auth...")
    headers = {"X-API-Key": "test_api_key_12345"}
    response = client.get("/api/clans/", headers=headers)
    # Should return 200 with empty array (no clans in test DB)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"✓ Clans endpoint works (returned {len(data)} clans)")


def test_openapi_docs():
    """Test that OpenAPI documentation is available"""
    print("\nTesting OpenAPI documentation...")
    response = client.get("/docs")
    assert response.status_code == 200
    print("✓ OpenAPI documentation is available")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("API Unit Tests")
    print("=" * 60)

    try:
        test_root()
        test_health()
        test_status_without_auth()
        test_status_with_auth()
        test_clans_without_auth()
        test_clans_with_auth()
        test_openapi_docs()

        print("\n" + "=" * 60)
        print("✅ All tests passed!")
        print("=" * 60)
        return True
    except AssertionError as e:
        print(f"\n❌ Test failed: {e}")
        return False
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
