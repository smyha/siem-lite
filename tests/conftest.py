"""
Pytest configuration and fixtures for SIEM Lite tests.
"""

import asyncio
import tempfile
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
try:
    import pytest_asyncio
    from fastapi.testclient import TestClient
    TESTING_AVAILABLE = True
except ImportError:
    TESTING_AVAILABLE = False

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False

if TESTING_AVAILABLE and SQLALCHEMY_AVAILABLE:
    from siem_lite.infrastructure.database import get_db
    from siem_lite.infrastructure.models import Base
    from siem_lite.main import app


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an instance of the default event loop for the test session."""
    if not TESTING_AVAILABLE:
        pytest.skip("Testing dependencies not available")
    
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def temp_db_file() -> Generator[Path, None, None]:
    """Create a temporary database file."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = Path(tmp.name)
    yield db_path
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def test_db_engine(temp_db_file: Path):
    """Create a test database engine."""
    if not SQLALCHEMY_AVAILABLE:
        pytest.skip("SQLAlchemy not available")
    
    engine = create_engine(
        f"sqlite:///{temp_db_file}",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_db_session(test_db_engine):
    """Create a test database session."""
    if not SQLALCHEMY_AVAILABLE:
        pytest.skip("SQLAlchemy not available")
    
    TestingSessionLocal = sessionmaker(
        autocommit=False, autoflush=False, bind=test_db_engine
    )
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def test_client(test_db_session) -> TestClient:
    """Create a test client with database override."""
    if not TESTING_AVAILABLE:
        pytest.skip("Testing dependencies not available")
    
    def override_get_db():
        try:
            yield test_db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture
def sample_alert_data():
    """Sample alert data for testing."""
    return {
        "alert_type": "SSH Brute-Force Attempt",
        "source_ip": "192.168.1.100",
        "details": "Detected 5 failed login attempts in 60 seconds"
    }


@pytest.fixture
def sample_log_entries():
    """Sample log entries for testing."""
    from datetime import datetime, timedelta
    
    base_time = datetime.now()
    return [
        {
            "log_type": "sshd",
            "ip": "192.168.1.100",
            "timestamp": base_time - timedelta(seconds=30),
            "status": "failed"
        },
        {
            "log_type": "nginx",
            "ip": "192.168.1.101",
            "status_code": 404,
            "timestamp": base_time - timedelta(seconds=20),
        },
        {
            "log_type": "sshd",
            "ip": "192.168.1.100",
            "timestamp": base_time - timedelta(seconds=10),
            "status": "failed"
        }
    ]


@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    from siem_lite.utils.config import Settings
    
    return Settings(
        debug=True,
        environment="testing",
        database__url="sqlite:///:memory:",
        api__host="127.0.0.1",
        api__port=8001,
    )
