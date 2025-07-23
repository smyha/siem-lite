"""
Tests for API endpoints.
"""

import pytest

try:
    from fastapi.testclient import TestClient
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing dependencies not available")
class TestAlertsAPI:
    """Test cases for alerts API."""
    
    def test_create_alert(self, test_client: TestClient, sample_alert_data):
        """Test creating a new alert."""
        response = test_client.post("/api/alerts", json=sample_alert_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["alert_type"] == sample_alert_data["alert_type"]
        assert data["source_ip"] == sample_alert_data["source_ip"]
        assert data["details"] == sample_alert_data["details"]
        assert "id" in data
        assert "timestamp" in data
    
    def test_create_alert_invalid_ip(self, test_client: TestClient):
        """Test creating alert with invalid IP address."""
        invalid_data = {
            "alert_type": "Test Alert",
            "source_ip": "invalid-ip",
            "details": "Test details"
        }
        
        response = test_client.post("/api/alerts", json=invalid_data)
        assert response.status_code == 422
    
    def test_get_alerts_empty(self, test_client: TestClient):
        """Test getting alerts when database is empty."""
        response = test_client.get("/api/alerts")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["items"] == []
        assert data["total"] == 0
    
    def test_get_alerts_with_data(self, test_client: TestClient, sample_alert_data):
        """Test getting alerts with existing data."""
        # Create an alert first
        create_response = test_client.post("/api/alerts", json=sample_alert_data)
        assert create_response.status_code == 201
        
        # Get all alerts
        response = test_client.get("/api/alerts")
        assert response.status_code == 200
        
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert len(data["items"]) == 1
        assert data["total"] == 1
        assert data["items"][0]["alert_type"] == sample_alert_data["alert_type"]
    
    def test_get_alert_by_id(self, test_client: TestClient, sample_alert_data):
        """Test getting a specific alert by ID."""
        # Create an alert first
        create_response = test_client.post("/api/alerts", json=sample_alert_data)
        created_alert = create_response.json()
        alert_id = created_alert["id"]
        
        # Get the specific alert
        response = test_client.get(f"/api/alerts/{alert_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["id"] == alert_id
        assert data["alert_type"] == sample_alert_data["alert_type"]
    
    def test_get_alert_not_found(self, test_client: TestClient):
        """Test getting a non-existent alert."""
        response = test_client.get("/api/alerts/999")
        assert response.status_code == 404


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing dependencies not available")
class TestHealthAPI:
    """Test cases for health API."""
    
    def test_health_check(self, test_client: TestClient):
        """Test health check endpoint."""
        response = test_client.get("/api/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert data["status"] == "healthy"
    
    def test_health_check_detailed(self, test_client: TestClient):
        """Test detailed health check."""
        response = test_client.get("/api/health?detailed=true")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "timestamp" in data
        assert "details" in data


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing dependencies not available")
class TestStatsAPI:
    """Test cases for statistics API."""
    
    def test_get_stats_empty(self, test_client: TestClient):
        """Test getting stats when no data exists."""
        response = test_client.get("/api/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_alerts" in data
        assert data["total_alerts"] == 0
    
    def test_get_stats_with_data(self, test_client: TestClient, sample_alert_data):
        """Test getting stats with existing data."""
        # Create an alert first
        create_response = test_client.post("/api/alerts", json=sample_alert_data)
        assert create_response.status_code == 201
        
        # Get stats
        response = test_client.get("/api/stats")
        assert response.status_code == 200
        
        data = response.json()
        assert data["total_alerts"] == 1


@pytest.mark.skipif(not TESTING_AVAILABLE, reason="Testing dependencies not available")
class TestRootAPI:
    """Test cases for root API."""
    
    def test_root_endpoint(self, test_client: TestClient):
        """Test root endpoint."""
        response = test_client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "SIEM Lite" in data["message"]


class TestSecurityFeatures:
    """Test security features."""
    
    def test_cors_headers(self, test_client: TestClient):
        """Test CORS headers are present."""
        if not TESTING_AVAILABLE:
            pytest.skip("Testing dependencies not available")
            
        response = test_client.get("/", headers={"Origin": "http://localhost:3000"})
        
        assert response.status_code == 200
        # CORS headers should be present
        assert "access-control-allow-origin" in response.headers
    
    def test_security_headers(self, test_client: TestClient):
        """Test security headers are present."""
        if not TESTING_AVAILABLE:
            pytest.skip("Testing dependencies not available")
            
        response = test_client.get("/")
        
        assert response.status_code == 200
        # Security headers should be present
        assert "x-content-type-options" in response.headers
        assert "x-frame-options" in response.headers
        assert "x-xss-protection" in response.headers
    
    def test_request_size_validation(self, test_client: TestClient):
        """Test request size validation."""
        if not TESTING_AVAILABLE:
            pytest.skip("Testing dependencies not available")
            
        # Test with large payload (this would be rejected by the middleware)
        large_data = {"data": "x" * 1000000}  # 1MB of data
        response = test_client.post("/api/alerts", json=large_data)
        
        # Should handle large requests gracefully
        assert response.status_code in [400, 413, 422]
