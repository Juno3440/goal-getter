"""
Pytest configuration for integration tests
"""

import os
import uuid

import pytest

# Set test mode for authentication
os.environ["TESTING"] = "true"

# Global test configuration - use dev database for all integration tests
# These should be set as environment variables, not hardcoded
if not os.environ.get("SUPABASE_URL"):
    raise ValueError("SUPABASE_URL environment variable must be set for tests")
if not os.environ.get("SUPABASE_KEY"):
    raise ValueError("SUPABASE_KEY environment variable must be set for tests")

# Test user for integration tests - use proper UUID format
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

# Additional test user UUIDs for tests that need multiple users
TEST_USER_IDS = {
    "user-123": "550e8400-e29b-41d4-a716-446655440001",
    "user-a": "550e8400-e29b-41d4-a716-446655440002", 
    "user-b": "550e8400-e29b-41d4-a716-446655440003",
}


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
    # Get all test user IDs
    all_test_user_ids = [TEST_USER_ID] + list(TEST_USER_IDS.values())
    
    # Clean up before test
    try:
        for user_id in all_test_user_ids:
            dev_supabase.table("goals").delete().eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")

    # Ensure test users exist in users table
    try:
        for user_id in all_test_user_ids:
            dev_supabase.table("users").upsert({
                "id": user_id,
                "email": f"test-{user_id}@example.com",
                "full_name": f"Test User {user_id}",
                "openai_sub": None
            }).execute()
    except Exception as e:
        print(f"User creation error: {e}")

    yield

    # Clean up after test
    try:
        for user_id in all_test_user_ids:
            dev_supabase.table("goals").delete().eq("user_id", user_id).execute()
    except Exception as e:
        print(f"Cleanup error: {e}")
