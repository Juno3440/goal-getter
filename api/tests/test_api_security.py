"""
API Security Tests for GoalGPT
Tests user isolation, JWT validation, and security boundaries.
"""

import os
import time
from unittest.mock import patch
from uuid import uuid4

from fastapi.testclient import TestClient
from jose import jwt

# Import the app
from api.main import AUDIENCE, JWT_SECRET, app

client = TestClient(app)


class TestJWTAuthentication:
    """Test JWT token validation and security."""

    def create_jwt_token(self, user_id: str, exp_offset: int = 3600) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + exp_offset, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    def test_access_without_token_fails(self):
        """Test that endpoints require authentication."""
        # Try to access protected endpoints without token
        response = client.get("/goals")
        assert response.status_code == 403  # FastAPI returns 403 for missing bearer token

        response = client.post("/goals", json={"title": "Test Goal"})
        assert response.status_code == 403

        response = client.get("/goals/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 403

    def test_invalid_token_fails(self):
        """Test that invalid tokens are rejected."""
        headers = {"Authorization": "Bearer invalid-token"}

        response = client.get("/goals", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication" in response.json()["detail"]

    def test_expired_token_fails(self):
        """Test that expired tokens are rejected."""
        # Create expired token (1 hour in the past)
        expired_token = self.create_jwt_token("user-123", exp_offset=-3600)
        headers = {"Authorization": "Bearer " + expired_token}

        response = client.get("/goals", headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication" in response.json()["detail"]

    def test_wrong_audience_fails(self):
        """Test that tokens with wrong audience are rejected."""
        payload = {"sub": "user-123", "aud": "wrong-audience", "exp": int(time.time()) + 3600, "iat": int(time.time())}
        wrong_aud_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        headers = {"Authorization": "Bearer " + wrong_aud_token}

        response = client.get("/goals", headers=headers)
        assert response.status_code == 401

    def test_token_without_subject_fails(self):
        """Test that tokens without user ID (sub claim) are rejected."""
        payload = {
            "aud": AUDIENCE,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time()),
            # Missing "sub" claim
        }
        no_sub_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        headers = {"Authorization": "Bearer " + no_sub_token}

        response = client.get("/goals", headers=headers)
        assert response.status_code == 401
        assert "User ID not found in token" in response.json()["detail"]

    @patch("api.db.get_all_goals")
    def test_valid_token_succeeds(self, mock_get_goals):
        """Test that valid tokens allow access."""
        mock_get_goals.return_value = []

        valid_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + valid_token}

        response = client.get("/goals", headers=headers)
        assert response.status_code == 200
        mock_get_goals.assert_called_once_with("user-123")


class TestUserIsolation:
    """Test that users can only access their own data."""

    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @patch("api.db.get_all_goals")
    def test_user_can_only_access_own_goals(self, mock_get_goals):
        """Test that user A cannot access user B's goals."""
        user_a_token = self.create_jwt_token("user-a")
        user_b_token = self.create_jwt_token("user-b")

        mock_get_goals.return_value = []

        # User A requests goals
        headers_a = {"Authorization": "Bearer " + user_a_token}
        response = client.get("/goals", headers=headers_a)
        assert response.status_code == 200
        mock_get_goals.assert_called_with("user-a")

        # User B requests goals
        headers_b = {"Authorization": "Bearer " + user_b_token}
        response = client.get("/goals", headers=headers_b)
        assert response.status_code == 200
        mock_get_goals.assert_called_with("user-b")

        # Verify each user's ID was used in separate calls
        assert mock_get_goals.call_count == 2

    @patch("api.db.create_goal")
    def test_user_can_only_create_goals_for_themselves(self, mock_create_goal):
        """Test that goal creation is isolated to the authenticated user."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}

        mock_create_goal.return_value = {"id": "goal-123", "title": "Test Goal", "user_id": "user-123"}

        response = client.post("/goals", json={"title": "Test Goal"}, headers=headers)

        assert response.status_code == 201
        mock_create_goal.assert_called_once_with("user-123", "Test Goal", None)

    @patch("api.db.get_all_goals")
    def test_goal_access_by_id_respects_user_ownership(self, mock_get_goals):
        """Test that users can only access their own goals by ID."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}

        # Use a proper UUID for the goal ID
        goal_uuid = str(uuid4())

        # Mock user's goals (should contain the goal we're looking for)
        mock_get_goals.return_value = [{"id": goal_uuid, "title": "User's Goal", "user_id": "user-123", "children": []}]

        # Request specific goal
        response = client.get(f"/goals/{goal_uuid}", headers=headers)
        assert response.status_code == 200

        # Verify the database was queried with correct user ID
        mock_get_goals.assert_called_once_with("user-123")


class TestInputValidation:
    """Test input validation and sanitization."""

    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @patch("api.db.create_goal")
    def test_invalid_goal_status_rejected(self, mock_create_goal):
        """Test that invalid status values are rejected."""
        # Use a proper UUID for user ID instead of "user-123"
        user_id = str(uuid4())
        user_token = self.create_jwt_token(user_id)
        headers = {"Authorization": "Bearer " + user_token}

        # Mock the create_goal function so we don't hit the real database
        mock_create_goal.return_value = {"id": "test-goal", "title": "Test Goal", "user_id": user_id}

        # The GoalCreate model doesn't have a status field, so this should fail validation
        # Try to create goal with an invalid field (status not allowed in creation)
        response = client.post("/goals", json={"title": "Test Goal", "status": "invalid-status"}, headers=headers)

        # Should return 422 because status field is not part of GoalCreate model
        assert response.status_code == 422  # Pydantic validation error

    @patch("api.db.create_goal")
    def test_missing_title_rejected(self, mock_create_goal):
        """Test that goals without titles are rejected."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}

        # Mock the create_goal function
        mock_create_goal.return_value = {"id": "test-goal", "title": "", "user_id": "user-123"}

        response = client.post("/goals", json={}, headers=headers)

        assert response.status_code == 422  # Missing required field

    def test_invalid_uuid_format_rejected(self):
        """Test that invalid UUID formats are rejected."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}

        # Try to access goal with invalid UUID format
        response = client.get("/goals/not-a-uuid", headers=headers)
        assert response.status_code == 422  # Validation error

    @patch("api.db.update_goal")
    def test_update_goal_validates_status(self, mock_update_goal):
        """Test that goal updates validate status values."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}

        # Mock the update_goal function
        mock_update_goal.return_value = {"id": "goal-123", "status": "done"}

        goal_uuid = str(uuid4())
        response = client.patch(f"/goals/{goal_uuid}", json={"status": "invalid-status"}, headers=headers)

        # Should return 422 for invalid status value
        assert response.status_code == 422


class TestAPIKeyEndpoint:
    """Test the GPT API key endpoint security."""

    @patch("api.db.get_all_goals")
    def test_gpt_endpoint_requires_valid_api_key(self, mock_get_goals):
        """Test that the GPT endpoint requires a valid API key."""
        mock_get_goals.return_value = []

        # Try without API key
        response = client.get("/gpt/goals")
        assert response.status_code == 401

        # Try with wrong API key
        headers = {"api-key": "wrong-key"}
        response = client.get("/gpt/goals", headers=headers)
        assert response.status_code == 401

    @patch("api.db.get_all_goals")
    @patch.dict(os.environ, {"GPT_API_KEY": "test-api-key", "DEFAULT_USER_ID": "default-user"})
    def test_gpt_endpoint_works_with_valid_key(self, mock_get_goals):
        """Test that the GPT endpoint works with valid API key."""
        mock_get_goals.return_value = []

        headers = {"api-key": "test-api-key"}
        response = client.get("/gpt/goals", headers=headers)
        assert response.status_code == 200
        mock_get_goals.assert_called_once_with("default-user")

    @patch("api.db.get_all_goals")
    @patch.dict(os.environ, {"GPT_API_KEY": "test-key"}, clear=False)
    def test_gpt_endpoint_fails_without_default_user(self, mock_get_goals):
        """Test that GPT endpoint fails if DEFAULT_USER_ID is not set."""
        # Remove DEFAULT_USER_ID from environment
        if "DEFAULT_USER_ID" in os.environ:
            del os.environ["DEFAULT_USER_ID"]

        mock_get_goals.return_value = []

        headers = {"api-key": "test-key"}
        response = client.get("/gpt/goals", headers=headers)

        # Should fail because DEFAULT_USER_ID is not configured
        assert response.status_code == 500


class TestRateLimiting:
    """Test rate limiting (placeholder for future implementation)."""

    def test_rate_limiting_placeholder(self):
        """Placeholder test for rate limiting functionality."""
        # Rate limiting not implemented yet, but this test documents the requirement
        # Future implementation should limit requests per user/IP
        assert True  # Placeholder


class TestErrorHandling:
    """Test error handling and information disclosure."""

    def test_error_messages_dont_leak_sensitive_info(self):
        """Test that error messages don't expose sensitive information."""
        # Test various error conditions to ensure they don't leak:
        # - Database connection strings
        # - Internal file paths
        # - Stack traces in production
        # - User data from other users

        # Invalid token should give generic error
        headers = {"Authorization": "Bearer invalid-token"}
        response = client.get("/goals", headers=headers)
        assert response.status_code == 401
        error_detail = response.json()["detail"]

        # Should not contain sensitive information
        assert "database" not in error_detail.lower()
        assert "supabase" not in error_detail.lower()
        assert "traceback" not in error_detail.lower()
        assert "file" not in error_detail.lower()
