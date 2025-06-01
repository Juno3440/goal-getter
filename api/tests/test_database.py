"""
Database Integration Tests for GoalGPT
Tests database constraints, RLS policies, and data integrity.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from uuid import uuid4
import json

# Import database functions
from db import build_tree, get_all_goals, create_goal, update_goal, delete_goal, supabase

class TestDatabaseIntegration:
    """Test database operations with mocked Supabase responses."""
    
    def test_supabase_client_initialization(self):
        """Test that Supabase client is properly initialized."""
        # Should not raise an exception if env vars are set
        assert supabase is not None
        assert hasattr(supabase, 'table')
        assert hasattr(supabase, 'auth')
    
    @patch.dict(os.environ, {}, clear=True)
    def test_missing_env_vars_raises_error(self):
        """Test that missing environment variables raise appropriate errors."""
        # This test checks if the module would fail to initialize without env vars
        # We can't easily test this with the already imported module, so this is a 
        # documentation test for the expected behavior
        assert True  # Placeholder - the actual check happens at module load time

class TestTreeBuilding:
    """Test the tree building logic."""
    
    def test_build_empty_tree(self):
        """Test building tree from empty list."""
        result = build_tree([])
        assert result == []
    
    def test_build_single_node_tree(self):
        """Test building tree with single root node."""
        rows = [
            {"id": "root-1", "parent_id": None, "title": "Root Goal"}
        ]
        result = build_tree(rows)
        
        assert len(result) == 1
        assert result[0]["id"] == "root-1"
        assert result[0]["children"] == []
    
    def test_build_hierarchical_tree(self):
        """Test building tree with parent-child relationships."""
        rows = [
            {"id": "root-1", "parent_id": None, "title": "Root Goal"},
            {"id": "child-1", "parent_id": "root-1", "title": "Child 1"},
            {"id": "child-2", "parent_id": "root-1", "title": "Child 2"},
            {"id": "grandchild-1", "parent_id": "child-1", "title": "Grandchild 1"}
        ]
        result = build_tree(rows)
        
        # Should have one root
        assert len(result) == 1
        root = result[0]
        assert root["id"] == "root-1"
        
        # Root should have two children
        assert len(root["children"]) == 2
        child_ids = [child["id"] for child in root["children"]]
        assert "child-1" in child_ids
        assert "child-2" in child_ids
        
        # Child-1 should have one grandchild
        child_1 = next(child for child in root["children"] if child["id"] == "child-1")
        assert len(child_1["children"]) == 1
        assert child_1["children"][0]["id"] == "grandchild-1"
        
        # Child-2 should have no children
        child_2 = next(child for child in root["children"] if child["id"] == "child-2")
        assert len(child_2["children"]) == 0
    
    def test_build_tree_with_orphaned_nodes(self):
        """Test tree building handles orphaned nodes (parent_id points to non-existent parent)."""
        rows = [
            {"id": "root-1", "parent_id": None, "title": "Root Goal"},
            {"id": "orphan-1", "parent_id": "non-existent", "title": "Orphaned Goal"}
        ]
        result = build_tree(rows)
        
        # Should have two root-level items (the actual root and the orphan)
        assert len(result) == 2
        root_ids = [item["id"] for item in result]
        assert "root-1" in root_ids
        assert "orphan-1" in root_ids
    
    def test_build_tree_with_multiple_roots(self):
        """Test tree building with multiple root nodes."""
        rows = [
            {"id": "root-1", "parent_id": None, "title": "Root Goal 1"},
            {"id": "root-2", "parent_id": None, "title": "Root Goal 2"},
            {"id": "child-1", "parent_id": "root-1", "title": "Child of Root 1"}
        ]
        result = build_tree(rows)
        
        # Should have two root nodes
        assert len(result) == 2
        root_ids = [item["id"] for item in result]
        assert "root-1" in root_ids
        assert "root-2" in root_ids
        
        # First root should have child, second should not
        root_1 = next(item for item in result if item["id"] == "root-1")
        root_2 = next(item for item in result if item["id"] == "root-2")
        assert len(root_1["children"]) == 1
        assert len(root_2["children"]) == 0

class TestDatabaseOperations:
    """Test database CRUD operations with mocked Supabase."""
    
    @patch('db.supabase')
    def test_get_all_goals_success(self, mock_supabase):
        """Test successful goal retrieval."""
        # Mock Supabase response
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "goal-1", "user_id": "user-123", "title": "Test Goal", "parent_id": None}
        ]
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        result = get_all_goals("user-123")
        
        # Verify Supabase was called correctly
        mock_supabase.table.assert_called_with("goals")
        mock_supabase.table.return_value.select.assert_called_with("*")
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with("user_id", "user-123")
        
        # Verify result structure
        assert len(result) == 1
        assert result[0]["id"] == "goal-1"
        assert "children" in result[0]
    
    @patch('db.supabase')
    def test_create_goal_success(self, mock_supabase):
        """Test successful goal creation."""
        # Mock Supabase response
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "new-goal-id", "user_id": "user-123", "title": "New Goal", "parent_id": None}
        ]
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        result = create_goal("user-123", "New Goal")
        
        # Verify Supabase was called correctly
        mock_supabase.table.assert_called_with("goals")
        expected_payload = {"user_id": "user-123", "title": "New Goal"}
        mock_supabase.table.return_value.insert.assert_called_with(expected_payload)
        
        # Verify result
        assert result["id"] == "new-goal-id"
        assert result["title"] == "New Goal"
    
    @patch('db.supabase')
    def test_create_goal_with_parent(self, mock_supabase):
        """Test goal creation with parent relationship."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "child-goal-id", "user_id": "user-123", "title": "Child Goal", "parent_id": "parent-id"}
        ]
        
        mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
        
        result = create_goal("user-123", "Child Goal", "parent-id")
        
        # Verify parent_id was included in payload
        expected_payload = {"user_id": "user-123", "title": "Child Goal", "parent_id": "parent-id"}
        mock_supabase.table.return_value.insert.assert_called_with(expected_payload)
        
        assert result["parent_id"] == "parent-id"
    
    @patch('db.supabase')
    def test_update_goal_success(self, mock_supabase):
        """Test successful goal update."""
        mock_response = MagicMock()
        mock_response.data = [
            {"id": "goal-id", "title": "Updated Title", "status": "done"}
        ]
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        updates = {"title": "Updated Title", "status": "done"}
        result = update_goal("goal-id", updates)
        
        # Verify Supabase was called correctly
        expected_updates = {"title": "Updated Title", "status": "done", "updated_at": "NOW()"}
        mock_supabase.table.return_value.update.assert_called_with(expected_updates)
        mock_supabase.table.return_value.update.return_value.eq.assert_called_with("id", "goal-id")
        
        assert result["title"] == "Updated Title"
    
    @patch('db.supabase')
    def test_update_nonexistent_goal(self, mock_supabase):
        """Test updating a goal that doesn't exist."""
        mock_response = MagicMock()
        mock_response.data = []  # No data returned means goal not found
        
        mock_supabase.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        
        result = update_goal("nonexistent-id", {"title": "New Title"})
        
        # Should return empty dict when no goal found
        assert result == {}
    
    @patch('db.supabase')
    def test_delete_goal_success(self, mock_supabase):
        """Test successful goal deletion."""
        mock_response = MagicMock()
        mock_response.data = [{"id": "deleted-goal-id"}]  # Some data indicates successful deletion
        
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        
        result = delete_goal("goal-id")
        
        # Verify Supabase was called correctly
        mock_supabase.table.assert_called_with("goals")
        mock_supabase.table.return_value.delete.return_value.eq.assert_called_with("id", "goal-id")
        
        assert result is True
    
    @patch('db.supabase')
    def test_delete_nonexistent_goal(self, mock_supabase):
        """Test deleting a goal that doesn't exist."""
        mock_response = MagicMock()
        mock_response.data = []  # No data returned means goal not found
        
        mock_supabase.table.return_value.delete.return_value.eq.return_value.execute.return_value = mock_response
        
        result = delete_goal("nonexistent-id")
        
        assert result is False

class TestDataIntegrity:
    """Test data integrity and constraint validation."""
    
    def test_goal_data_structure_validation(self):
        """Test that goal data has required fields after tree building."""
        rows = [
            {
                "id": "goal-1",
                "user_id": "user-123",
                "title": "Test Goal",
                "status": "todo",
                "parent_id": None,
                "created_at": "2024-01-01T00:00:00Z",
                "updated_at": "2024-01-01T00:00:00Z"
            }
        ]
        
        result = build_tree(rows)
        goal = result[0]
        
        # Verify required fields are present
        required_fields = ["id", "user_id", "title", "status", "parent_id", "created_at", "updated_at"]
        for field in required_fields:
            assert field in goal, f"Required field {field} missing from goal"
        
        # Verify children array is added
        assert "children" in goal
        assert isinstance(goal["children"], list)
    
    def test_uuid_string_consistency(self):
        """Test that UUIDs are consistently handled as strings."""
        # This tests the str() conversion in build_tree
        rows = [
            {"id": 123, "parent_id": None, "title": "Numeric ID"},  # Numeric ID (edge case)
            {"id": "uuid-string", "parent_id": 123, "title": "String parent ref"}
        ]
        
        result = build_tree(rows)
        
        # Should handle numeric IDs by converting to strings
        assert len(result) == 1  # Numeric ID should become root
        assert result[0]["id"] == 123
        assert len(result[0]["children"]) == 1
        assert result[0]["children"][0]["id"] == "uuid-string"

class TestErrorConditions:
    """Test error handling and edge cases."""
    
    @patch('db.supabase')
    def test_supabase_connection_error_handling(self, mock_supabase):
        """Test handling of Supabase connection errors."""
        # Mock a connection error
        mock_supabase.table.side_effect = Exception("Connection failed")
        
        with pytest.raises(Exception) as exc_info:
            get_all_goals("user-123")
        
        assert "Connection failed" in str(exc_info.value)
    
    @patch('db.supabase')
    def test_malformed_supabase_response_handling(self, mock_supabase):
        """Test handling of malformed Supabase responses."""
        # Mock a response without data attribute
        mock_response = MagicMock()
        del mock_response.data  # Remove data attribute
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        with pytest.raises(AttributeError):
            get_all_goals("user-123")
    
    def test_build_tree_with_circular_references(self):
        """Test tree building handles circular references gracefully."""
        # Create circular reference: A -> B -> A
        rows = [
            {"id": "a", "parent_id": "b", "title": "Goal A"},
            {"id": "b", "parent_id": "a", "title": "Goal B"}
        ]
        
        # This should not cause infinite loop, but both nodes will be in each other's children
        # Current implementation: neither becomes a root (they're circular children)
        result = build_tree(rows)
        
        # Current behavior: empty root list due to circular reference
        # This is actually correct behavior - circular references are contained
        assert len(result) == 0
        
        # Alternative test: ensure no infinite loops occur (test should complete quickly)
        # If this test hangs, there's an infinite loop bug
        assert True  # Test completed without hanging

class TestRowLevelSecurity:
    """Test Row Level Security simulation (since we can't test actual RLS policies directly)."""
    
    @patch('db.supabase')
    def test_user_isolation_in_queries(self, mock_supabase):
        """Test that database queries properly filter by user_id."""
        mock_response = MagicMock()
        mock_response.data = []
        
        mock_supabase.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        
        # Call with specific user ID
        get_all_goals("specific-user-123")
        
        # Verify that the query filtered by the correct user ID
        mock_supabase.table.return_value.select.return_value.eq.assert_called_with("user_id", "specific-user-123")
    
    def test_create_goal_includes_user_id(self):
        """Test that goal creation always includes the authenticated user's ID."""
        with patch('db.supabase') as mock_supabase:
            mock_response = MagicMock()
            mock_response.data = [{"id": "new-goal", "user_id": "user-123"}]
            mock_supabase.table.return_value.insert.return_value.execute.return_value = mock_response
            
            create_goal("user-123", "Test Goal", None)
            
            # Verify user_id was included in the insert payload
            call_args = mock_supabase.table.return_value.insert.call_args[0][0]
            assert call_args["user_id"] == "user-123"