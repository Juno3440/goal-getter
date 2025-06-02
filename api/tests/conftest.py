"""
Pytest configuration for integration tests
"""

import os

import pytest

# Global test configuration - use dev database for all integration tests
os.environ["SUPABASE_URL"] = "https://tstnyxldiqfbcvzxtzxi.supabase.co"
os.environ["SUPABASE_KEY"] = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdG55eGxkaXFmYmN2enh0enhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4ODY5MTgsImV4cCI6MjA2NDQ2MjkxOH0.qinSNo9vUvAEQsrJcESBjmUnJWagJbSX0RguxjMr1C0"
)

# Test user for integration tests
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture(scope="session", autouse=True)
def setup_dev_environment():
    """Set up dev environment for all tests"""
    print(f"Using DEV database: {os.environ['SUPABASE_URL']}")
    yield


@pytest.fixture
def dev_supabase():
    """Provide a supabase client configured for dev environment"""
    from supabase import create_client

    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])


@pytest.fixture(autouse=True)
def cleanup_test_data(dev_supabase):
    """Clean up test data before and after each test using dev supabase client"""
    # Clean up before test
    try:
        dev_supabase.table("goals").delete().eq("user_id", TEST_USER_ID).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")

    yield

    # Clean up after test
    try:
        dev_supabase.table("goals").delete().eq("user_id", TEST_USER_ID).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")
