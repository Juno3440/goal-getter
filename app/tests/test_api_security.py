"""
API Security Tests for GoalGPT
Tests user isolation, JWT validation, and security boundaries.
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from jose import jwt
import time
from uuid import uuid4

# Import the app
from app.main import app, JWT_SECRET, AUDIENCE

client = TestClient(app)

class TestJWTAuthentication:
    """Test JWT token validation and security."""
    
    def create_jwt_token(self, user_id: str, exp_offset: int = 3600) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {
            "sub": user_id,
            "aud": AUDIENCE,
            "exp": int(time.time()) + exp_offset,
            "iat": int(time.time())
        }
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
        payload = {
            "sub": "user-123",
            "aud": "wrong-audience",
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        }
        wrong_aud_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        headers = {"Authorization": "Bearer " + wrong_aud_token}
        
        response = client.get("/goals", headers=headers)
        assert response.status_code == 401
    
    def test_token_without_subject_fails(self):
        """Test that tokens without user ID (sub claim) are rejected."""
        payload = {
            "aud": AUDIENCE,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
            # Missing "sub" claim
        }
        no_sub_token = jwt.encode(payload, JWT_SECRET, algorithm="HS256")
        headers = {"Authorization": "Bearer " + no_sub_token}
        
        response = client.get("/goals", headers=headers)
        assert response.status_code == 401
        assert "User ID not found in token" in response.json()["detail"]
    
    @patch('app.db.get_all_goals')
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
        payload = {
            "sub": user_id,
            "aud": AUDIENCE,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    @patch('app.db.get_all_goals')
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
    
    @patch('app.db.create_goal')
    def test_user_can_only_create_goals_for_themselves(self, mock_create_goal):
        """Test that goal creation is isolated to the authenticated user."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}
        
        mock_create_goal.return_value = {"id": "goal-123", "title": "Test Goal", "user_id": "user-123"}
        
        response = client.post("/goals", 
                             json={"title": "Test Goal"}, 
                             headers=headers)
        
        assert response.status_code == 201
        mock_create_goal.assert_called_once_with("user-123", "Test Goal", None)
    
    @patch('app.db.get_all_goals')
    def test_goal_access_by_id_respects_user_ownership(self, mock_get_goals):
        """Test that users can only access their own goals by ID."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}
        
        # Mock user's goals (should contain the goal we're looking for)
        mock_get_goals.return_value = [
            {
                "id": "goal-456",
                "title": "User's Goal",
                "user_id": "user-123",
                "children": []
            }
        ]
        
        # Request specific goal
        response = client.get("/goals/goal-456", headers=headers)
        assert response.status_code == 200
        
        # Verify the database was queried with correct user ID
        mock_get_goals.assert_called_once_with("user-123")

class TestInputValidation:
    """Test input validation and sanitization."""
    
    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {
            "sub": user_id,
            "aud": AUDIENCE,
            "exp": int(time.time()) + 3600,
            "iat": int(time.time())
        }
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")
    
    def test_invalid_goal_status_rejected(self):
        """Test that invalid status values are rejected."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}
        
        # Try to create goal with invalid status
        response = client.post("/goals", 
                             json={"title": "Test Goal", "status": "invalid-status"}, 
                             headers=headers)
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_missing_title_rejected(self):
        """Test that goals without titles are rejected."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}
        
        response = client.post("/goals", 
                             json={}, 
                             headers=headers)
        
        assert response.status_code == 422  # Missing required field
    
    def test_invalid_uuid_format_rejected(self):
        """Test that invalid UUID formats are rejected."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}
        
        response = client.get("/goals/not-a-valid-uuid", headers=headers)
        assert response.status_code == 422  # Invalid UUID format
    
    @patch('app.db.update_goal')
    def test_update_goal_validates_status(self, mock_update_goal):
        """Test that goal updates validate status field."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": "Bearer " + user_token}
        
        valid_goal_id = str(uuid4())
        
        # Valid status update
        response = client.patch(f"/goals/{valid_goal_id}", 
                              json={"status": "done"}, 
                              headers=headers)
        # Should not fail validation (though might fail if goal doesn't exist)
        assert response.status_code in [200, 404]
        
        # Invalid status update
        response = client.patch(f"/goals/{valid_goal_id}", 
                              json={"status": "invalid"}, 
                              headers=headers)
        assert response.status_code == 422

class TestAPIKeyEndpoint:
    """Test the GPT API key endpoint security."""
    
    @patch('app.db.get_all_goals')
    def test_gpt_endpoint_requires_valid_api_key(self, mock_get_goals):
        """Test that GPT endpoint requires valid API key."""
        # Test without API key
        response = client.get("/gpt/goals")
        assert response.status_code == 401
        assert "Invalid API key" in response.json()["detail"]
        
        # Test with wrong API key
        headers = {"api-key": "wrong-key"}
        response = client.get("/gpt/goals", headers=headers)
        assert response.status_code == 401
    
    @patch('app.db.get_all_goals')
    @patch.dict(os.environ, {'GPT_API_KEY': 'test-api-key', 'DEFAULT_USER_ID': 'default-user'})
    def test_gpt_endpoint_works_with_valid_key(self, mock_get_goals):
        """Test that GPT endpoint works with valid API key."""
        mock_get_goals.return_value = []
        
        headers = {"api-key": "test-api-key"}
        response = client.get("/gpt/goals", headers=headers)
        
        assert response.status_code == 200
        mock_get_goals.assert_called_once_with("default-user")
    
    @patch.dict(os.environ, {'GPT_API_KEY': 'test-key'}, clear=False)
    def test_gpt_endpoint_fails_without_default_user(self):
        """Test that GPT endpoint fails if DEFAULT_USER_ID is not configured."""
        # Remove DEFAULT_USER_ID if it exists
        if 'DEFAULT_USER_ID' in os.environ:
            del os.environ['DEFAULT_USER_ID']
        
        headers = {"api-key": "test-key"}
        response = client.get("/gpt/goals", headers=headers)
        
        assert response.status_code == 500
        assert "DEFAULT_USER_ID environment variable not configured" in response.json()["detail"]

class TestRateLimiting:
    """Test rate limiting and abuse prevention (placeholder for future implementation)."""
    
    def test_rate_limiting_placeholder(self):
        """Placeholder test for rate limiting functionality."""
        # TODO: Implement rate limiting tests when rate limiting is added
        # For now, this serves as a reminder that rate limiting should be implemented
        assert True

class TestErrorHandling:
    """Test error handling and information disclosure."""
    
    def test_error_messages_dont_leak_sensitive_info(self):
        """Test that error messages don't expose sensitive information."""
        # Test with malformed token
        headers = {"Authorization": "Bearer malformed.token.here"}
        response = client.get("/goals", headers=headers)
        
        # Should return generic auth error, not detailed JWT parsing errors
        assert response.status_code == 401
        assert "Invalid authentication" in response.json()["detail"]
        # Should not contain internal error details
        assert "JWT" not in response.json()["detail"].lower()
        assert "decode" not in response.json()["detail"].lower()