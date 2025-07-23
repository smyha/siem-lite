"""
Tests for domain entities.
"""

import pytest
from datetime import datetime

try:
    from siem_lite.domain.entities import Alert
    ENTITIES_AVAILABLE = True
except ImportError:
    ENTITIES_AVAILABLE = False


@pytest.mark.skipif(not ENTITIES_AVAILABLE, reason="Domain entities not available")
class TestAlert:
    """Test cases for Alert entity."""
    
    def test_alert_creation(self):
        """Test alert creation with valid data."""
        alert = Alert(
            id=1,
            alert_type="SSH Brute-Force Attempt",
            source_ip="192.168.1.100",
            details="Multiple failed login attempts",
            timestamp=datetime.now()
        )
        
        assert alert.id == 1
        assert alert.alert_type == "SSH Brute-Force Attempt"
        assert alert.source_ip == "192.168.1.100"
        assert alert.details == "Multiple failed login attempts"
        assert isinstance(alert.timestamp, datetime)
    
    def test_alert_without_id(self):
        """Test alert creation without ID (for new alerts)."""
        alert = Alert(
            id=None,
            alert_type="Web Attack",
            source_ip="10.0.0.1",
            details="Suspicious HTTP requests"
        )
        
        assert alert.id is None
        assert alert.alert_type == "Web Attack"
        assert alert.source_ip == "10.0.0.1"
    
    def test_alert_string_representation(self):
        """Test alert string representation."""
        alert = Alert(
            id=1,
            alert_type="Test Alert",
            source_ip="192.168.1.1",
            details="Test details"
        )
        
        str_repr = str(alert)
        assert "Test Alert" in str_repr
        assert "192.168.1.1" in str_repr


class TestValidation:
    """Test cases for validation utilities."""
    
    def test_ip_validation(self):
        """Test IP address validation."""
        from siem_lite.utils.validation import validate_ip_address, ValidationError
        
        # Valid IP addresses
        assert validate_ip_address("192.168.1.1") == "192.168.1.1"
        assert validate_ip_address("10.0.0.1") == "10.0.0.1"
        assert validate_ip_address("2001:db8::1") == "2001:db8::1"
        
        # Invalid IP addresses
        with pytest.raises(ValidationError):
            validate_ip_address("invalid.ip")
        
        with pytest.raises(ValidationError):
            validate_ip_address("999.999.999.999")
    
    def test_alert_type_validation(self):
        """Test alert type validation."""
        from siem_lite.utils.validation import validate_alert_type, ValidationError
        
        # Valid alert types
        assert validate_alert_type("SSH Attack") == "SSH Attack"
        assert validate_alert_type("  Web Attack  ") == "Web Attack"
        
        # Invalid alert types
        with pytest.raises(ValidationError):
            validate_alert_type("")
        
        with pytest.raises(ValidationError):
            validate_alert_type("   ")
        
        with pytest.raises(ValidationError):
            validate_alert_type("a" * 101)  # Too long
    
    def test_status_code_validation(self):
        """Test HTTP status code validation."""
        from siem_lite.utils.validation import validate_status_code, ValidationError
        
        # Valid status codes
        assert validate_status_code(200) == 200
        assert validate_status_code("404") == 404
        assert validate_status_code(500) == 500
        
        # Invalid status codes
        with pytest.raises(ValidationError):
            validate_status_code(99)  # Too low
        
        with pytest.raises(ValidationError):
            validate_status_code(600)  # Too high
        
        with pytest.raises(ValidationError):
            validate_status_code("invalid")
    
    def test_username_validation(self):
        """Test username validation."""
        from siem_lite.utils.validation import validate_username, ValidationError
        
        # Valid usernames
        assert validate_username("admin") == "admin"
        assert validate_username("user123") == "user123"
        assert validate_username("test_user") == "test_user"
        assert validate_username("user.name") == "user.name"
        
        # Invalid usernames
        with pytest.raises(ValidationError):
            validate_username("")
        
        with pytest.raises(ValidationError):
            validate_username("a" * 51)  # Too long
        
        with pytest.raises(ValidationError):
            validate_username("user@domain")  # Invalid character
    
    def test_input_sanitization(self):
        """Test input sanitization."""
        from siem_lite.utils.validation import sanitize_user_input, ValidationError
        
        # Valid input
        assert sanitize_user_input("normal text") == "normal text"
        assert sanitize_user_input("  spaced  ") == "spaced"
        
        # Sanitized input
        assert sanitize_user_input("text<script>") == "textscript"
        assert sanitize_user_input('text"quote') == "textquote"
        
        # Invalid input
        with pytest.raises(ValidationError):
            sanitize_user_input("a" * 1001)  # Too long
        
        with pytest.raises(ValidationError):
            sanitize_user_input(123)  # Not a string
