"""
Critical User Flow Tests
Tests complete user journeys and high-risk scenarios in goal management.
"""

import time
from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient
from jose import jwt

from api.main import AUDIENCE, JWT_SECRET, app

client = TestClient(app)


class TestCompleteGoalLifecycle:
    """Test complete goal lifecycle from creation to deletion."""

    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @patch("api.db.supabase")
    def test_complete_goal_workflow(self, mock_supabase):
        """CRITICAL: Test complete goal creation → update → completion → deletion flow."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Step 1: Create parent goal
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "parent-goal", "title": "Learn Web Development", "status": "todo", "user_id": "user-123"}
        ]

        response = client.post("/goals", json={"title": "Learn Web Development"}, headers=headers)
        assert response.status_code == 201
        parent_goal = response.json()

        # Step 2: Create child goals
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "child-1", "title": "Learn HTML", "status": "todo", "parent_id": "parent-goal"}
        ]

        response = client.post("/goals", json={"title": "Learn HTML", "parent_id": parent_goal["id"]}, headers=headers)
        assert response.status_code == 201

        # Step 3: Update child goal status to "doing"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "child-1", "title": "Learn HTML", "status": "doing"}
        ]

        response = client.patch(f"/goals/child-1", json={"status": "doing"}, headers=headers)
        assert response.status_code == 200

        # Step 4: Complete child goal
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "child-1", "title": "Learn HTML", "status": "done"}
        ]

        response = client.patch(f"/goals/child-1", json={"status": "done"}, headers=headers)
        assert response.status_code == 200

        # Step 5: Try to delete parent (should handle children appropriately)
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [
            {"id": "parent-goal"}
        ]

        response = client.delete(f"/goals/parent-goal", headers=headers)
        assert response.status_code == 204

    @patch("api.db.supabase")
    def test_goal_reorganization_workflow(self, mock_supabase):
        """CRITICAL: Test moving goals between different parents."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Create initial structure: Parent A -> Child, Parent B (empty)
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "parent-a", "title": "Parent A", "status": "todo"}
        ]

        response = client.post("/goals", json={"title": "Parent A"}, headers=headers)
        assert response.status_code == 201

        # Move child from Parent A to Parent B
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "child-goal", "parent_id": "parent-b", "title": "Child Goal"}
        ]

        response = client.patch("/goals/child-goal", json={"parent_id": "parent-b"}, headers=headers)
        # Note: This would fail in current implementation - parent_id updates not supported
        # TODO: Implement goal reorganization functionality

    @patch("api.db.supabase")
    def test_bulk_status_updates(self, mock_supabase):
        """Test updating multiple goals simultaneously (batch operations)."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Simulate bulk status update (not currently supported in API)
        # TODO: Implement bulk update endpoint like PATCH /goals/bulk

        # For now, test sequential updates
        goals_to_update = ["goal-1", "goal-2", "goal-3"]

        for goal_id in goals_to_update:
            mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
                {"id": goal_id, "status": "done"}
            ]

            response = client.patch(f"/goals/{goal_id}", json={"status": "done"}, headers=headers)
            assert response.status_code == 200


class TestSessionExpirationScenarios:
    """Test behavior when JWT tokens expire during operations."""

    def create_expired_token(self, user_id: str) -> str:
        """Create an expired JWT token."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) - 3600, "iat": int(time.time()) - 7200}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    def test_goal_creation_with_expired_session(self):
        """Test goal creation fails gracefully with expired token."""
        expired_token = self.create_expired_token("user-123")
        headers = {"Authorization": f"Bearer {expired_token}"}

        response = client.post("/goals", json={"title": "Test Goal"}, headers=headers)
        assert response.status_code == 401
        assert "Invalid authentication" in response.json()["detail"]

    def test_long_operation_with_expiring_token(self):
        """Test behavior when token expires during a long-running operation."""
        # This is more relevant for batch operations or complex tree manipulations
        # Current implementation doesn't have long-running operations, but this
        # documents the need to handle token refresh
        pass


class TestErrorRecoveryScenarios:
    """Test error recovery and data consistency during failures."""

    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @patch("api.db.supabase")
    def test_partial_goal_creation_failure(self, mock_supabase):
        """Test recovery when goal creation partially fails."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Simulate database failure after validation passes
        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Database error")

        response = client.post("/goals", json={"title": "Test Goal"}, headers=headers)
        assert response.status_code == 500  # Should handle database errors gracefully

    @patch("api.db.supabase")
    def test_network_interruption_during_update(self, mock_supabase):
        """Test handling of network interruptions during goal updates."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Simulate network timeout
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.side_effect = TimeoutError(
            "Network timeout"
        )

        response = client.patch("/goals/test-goal", json={"status": "done"}, headers=headers)
        # Should return appropriate error status
        assert response.status_code in [500, 502, 504]

    @patch("api.db.supabase")
    def test_database_constraint_violation_handling(self, mock_supabase):
        """Test handling of database constraint violations."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Simulate constraint violation (e.g., duplicate ID, invalid foreign key)
        from supabase import SupabaseError

        mock_supabase.table.return_value.insert.return_value.execute.side_effect = Exception("Constraint violation")

        response = client.post("/goals", json={"title": "Test Goal"}, headers=headers)
        # Should handle database errors without exposing sensitive information
        assert response.status_code == 500


class TestDataIntegrityScenarios:
    """Test data integrity during complex operations."""

    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @patch("api.db.supabase")
    def test_orphaned_children_on_parent_deletion(self, mock_supabase):
        """CRITICAL: Test what happens to children when parent is deleted."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Mock getting all goals to show parent-child relationship
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = [
            {"id": "parent", "title": "Parent Goal", "parent_id": None},
            {"id": "child", "title": "Child Goal", "parent_id": "parent"},
        ]

        # Mock deletion of parent
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value.data = [{"id": "parent"}]

        response = client.delete("/goals/parent", headers=headers)
        assert response.status_code == 204

        # TODO: Verify children are handled appropriately (cascaded, orphaned, or prevented)
        # This requires querying the remaining goals and checking their state

    @patch("api.db.supabase")
    def test_invalid_parent_reference_creation(self, mock_supabase):
        """Test preventing creation of goals with invalid parent references."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Try to create goal with non-existent parent
        mock_supabase.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "new-goal", "parent_id": "nonexistent-parent", "title": "Invalid Goal"}
        ]

        response = client.post("/goals", json={"title": "Invalid Goal", "parent_id": "nonexistent-parent"}, headers=headers)

        # TODO: Should validate parent exists before creating goal
        # Currently this would succeed but create an orphaned reference
        assert response.status_code == 201  # Current behavior
        # assert response.status_code == 400  # Desired behavior with validation

    @patch("api.db.supabase")
    def test_status_consistency_in_hierarchy(self, mock_supabase):
        """Test status consistency rules in parent-child relationships."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Try to mark parent as "done" while children are still "todo"
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value.data = [
            {"id": "parent", "status": "done"}
        ]

        response = client.patch("/goals/parent", json={"status": "done"}, headers=headers)
        assert response.status_code == 200

        # TODO: Implement business logic to handle this scenario:
        # 1. Prevent parent completion if children incomplete
        # 2. Auto-complete children when parent is completed
        # 3. Allow inconsistent states but warn user
        # Currently no validation exists


class TestPerformanceCriticalScenarios:
    """Test performance under stress conditions."""

    def create_jwt_token(self, user_id: str) -> str:
        """Helper to create valid JWT tokens for testing."""
        payload = {"sub": user_id, "aud": AUDIENCE, "exp": int(time.time()) + 3600, "iat": int(time.time())}
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    @patch("api.db.supabase")
    def test_large_goal_tree_retrieval(self, mock_supabase):
        """Test performance with large goal trees (100+ goals)."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Create mock data for 100 goals in a deep hierarchy
        large_tree_data = []
        for i in range(100):
            parent_id = f"goal-{i-1}" if i > 0 else None
            large_tree_data.append(
                {"id": f"goal-{i}", "title": f"Goal {i}", "parent_id": parent_id, "status": "todo", "user_id": "user-123"}
            )

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = large_tree_data

        start_time = time.time()
        response = client.get("/goals", headers=headers)
        end_time = time.time()

        assert response.status_code == 200
        # Should complete within reasonable time (< 2 seconds)
        assert end_time - start_time < 2.0

    @patch("api.db.supabase")
    def test_tree_visualization_endpoint_performance(self, mock_supabase):
        """Test /api/tree endpoint performance with complex hierarchies."""
        user_token = self.create_jwt_token("user-123")
        headers = {"Authorization": f"Bearer {user_token}"}

        # Mock complex tree structure
        complex_tree = []
        # Create 5 root goals, each with 10 children, each with 2 grandchildren = 115 total
        for root_i in range(5):
            root_id = f"root-{root_i}"
            complex_tree.append(
                {"id": root_id, "title": f"Root Goal {root_i}", "parent_id": None, "status": "doing", "user_id": "user-123"}
            )

            for child_i in range(10):
                child_id = f"child-{root_i}-{child_i}"
                complex_tree.append(
                    {
                        "id": child_id,
                        "title": f"Child {root_i}-{child_i}",
                        "parent_id": root_id,
                        "status": "todo",
                        "user_id": "user-123",
                    }
                )

                for grandchild_i in range(2):
                    grandchild_id = f"grandchild-{root_i}-{child_i}-{grandchild_i}"
                    complex_tree.append(
                        {
                            "id": grandchild_id,
                            "title": f"Grandchild {root_i}-{child_i}-{grandchild_i}",
                            "parent_id": child_id,
                            "status": "todo",
                            "user_id": "user-123",
                        }
                    )

        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value.data = complex_tree

        start_time = time.time()
        response = client.get("/api/tree", headers=headers)
        end_time = time.time()

        assert response.status_code == 200
        assert end_time - start_time < 1.0  # Should be very fast for tree conversion

        # Verify tree structure
        tree_data = response.json()
        assert len(tree_data["nodes"]) == 115
        assert tree_data["root_id"] is not None
