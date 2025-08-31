import pytest
import httpx

# Fixture to provide an httpx client configured for the test service
# This fixture now assumes that the Docker services are already running.
@pytest.fixture
def client():
    """Provides an httpx client for making requests to the live service."""
    # The `httpx.Client` handles sessions and connection pooling
    with httpx.Client(base_url="http://localhost:8100") as c:
        yield c

