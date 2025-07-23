"""
Security utilities for SIEM Lite.
"""

import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

try:
    from jose import JWTError, jwt
    from passlib.context import CryptContext

    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    JWTError = Exception
    jwt = None

from .config import get_settings
from .exceptions import AuthenticationError, AuthorizationError, ValidationError

# Password hashing (fallback if passlib not available)
if JWT_AVAILABLE:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
else:
    pwd_context = None


def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    if pwd_context:
        return pwd_context.hash(password)
    else:
        # Fallback to basic hash (not recommended for production)
        return hashlib.sha256(password.encode()).hexdigest()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    if pwd_context:
        return pwd_context.verify(plain_password, hashed_password)
    else:
        # Fallback verification
        return hashlib.sha256(plain_password.encode()).hexdigest() == hashed_password


def generate_api_key() -> str:
    """Generate a secure API key."""
    return secrets.token_urlsafe(32)


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Create a JWT access token."""
    if not JWT_AVAILABLE:
        raise AuthenticationError("JWT library not available")

    settings = get_settings()
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(datetime.UTC) + expires_delta
    else:
        expire = datetime.now(datetime.UTC) + timedelta(
            minutes=settings.security.access_token_expire_minutes
        )

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.security.secret_key, algorithm=settings.security.algorithm
    )
    return encoded_jwt


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a JWT access token."""
    if not JWT_AVAILABLE:
        raise AuthenticationError("JWT library not available")

    settings = get_settings()

    try:
        payload = jwt.decode(
            token,
            settings.security.secret_key,
            algorithms=[settings.security.algorithm],
        )
        return payload
    except JWTError:
        raise AuthenticationError("Invalid token")


def hash_ip_address(ip: str) -> str:
    """Hash an IP address for privacy."""
    return hashlib.sha256(ip.encode()).hexdigest()[:16]


def rate_limit_key(ip: str, endpoint: str) -> str:
    """Generate a rate limiting key."""
    return f"rate_limit:{ip}:{endpoint}"


def generate_session_id() -> str:
    """Generate a secure session ID."""
    return secrets.token_urlsafe(32)


def generate_csrf_token() -> str:
    """Generate a CSRF token."""
    return secrets.token_urlsafe(32)


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal attacks."""
    # Remove directory traversal attempts
    filename = filename.replace("..", "").replace("/", "").replace("\\", "")

    # Remove potentially dangerous characters
    dangerous_chars = ["<", ">", ":", '"', "|", "?", "*"]
    for char in dangerous_chars:
        filename = filename.replace(char, "_")

    return filename.strip()


def is_safe_redirect_url(url: str, allowed_hosts: list) -> bool:
    """Check if a redirect URL is safe."""
    if not url:
        return False

    # Check for absolute URLs pointing to disallowed hosts
    if url.startswith(("http://", "https://")):
        from urllib.parse import urlparse

        parsed = urlparse(url)
        return parsed.netloc in allowed_hosts

    # Relative URLs are generally safe
    return not url.startswith("//")


class SecurityMiddleware:
    """Security middleware for request validation."""

    def __init__(self):
        self.settings = get_settings()

    def validate_request_size(self, content_length: int) -> None:
        """Validate request size."""
        max_size = 10 * 1024 * 1024  # 10MB
        if content_length > max_size:
            raise ValidationError("Request too large")

    def validate_content_type(self, content_type: str, allowed_types: list) -> None:
        """Validate content type."""
        if content_type not in allowed_types:
            raise ValidationError(f"Invalid content type: {content_type}")

    def sanitize_headers(self, headers: Dict[str, str]) -> Dict[str, str]:
        """Sanitize request headers."""
        dangerous_headers = ["x-forwarded-host", "x-original-url"]
        return {k: v for k, v in headers.items() if k.lower() not in dangerous_headers}

    def check_rate_limit(self, ip: str, endpoint: str) -> bool:
        """Check if request should be rate limited."""
        # Simple in-memory rate limiting (replace with Redis in production)
        key = rate_limit_key(ip, endpoint)
        # Implementation would depend on your chosen rate limiting backend
        return True  # Placeholder

    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key."""
        if not api_key:
            return False

        # In production, validate against database
        # For now, check against environment variable
        import os

        valid_key = os.getenv("SIEM_API_KEY")
        return api_key == valid_key if valid_key else False


class InputSanitizer:
    """Input sanitization utilities."""

    @staticmethod
    def sanitize_sql_input(input_str: str) -> str:
        """Sanitize input to prevent SQL injection."""
        # Remove SQL metacharacters
        dangerous_chars = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        for char in dangerous_chars:
            input_str = input_str.replace(char, "")
        return input_str.strip()

    @staticmethod
    def sanitize_command_input(input_str: str) -> str:
        """Sanitize input to prevent command injection."""
        # Remove command injection metacharacters
        dangerous_chars = [
            "&",
            "|",
            ";",
            "$",
            "`",
            ">",
            "<",
            "(",
            ")",
            "{",
            "}",
            "[",
            "]",
        ]
        for char in dangerous_chars:
            input_str = input_str.replace(char, "")
        return input_str.strip()

    @staticmethod
    def sanitize_path_input(path_str: str) -> str:
        """Sanitize path input to prevent path traversal."""
        # Remove path traversal attempts
        path_str = path_str.replace("..", "").replace("//", "/")

        # Remove null bytes
        path_str = path_str.replace("\x00", "")

        return path_str.strip()


def encrypt_sensitive_data(data: str, key: Optional[str] = None) -> str:
    """Encrypt sensitive data (placeholder - implement with proper crypto)."""
    if not key:
        key = get_settings().security.secret_key

    # This is a placeholder - use proper encryption in production
    return hashlib.sha256(f"{data}{key}".encode()).hexdigest()


def decrypt_sensitive_data(encrypted_data: str, key: Optional[str] = None) -> str:
    """Decrypt sensitive data (placeholder - implement with proper crypto)."""
    # This is a placeholder - implement proper decryption
    return encrypted_data  # Not actually decrypting for security
