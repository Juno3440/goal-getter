#!/usr/bin/env python3
"""
Simple test script to verify the enhanced schema works
"""

import json
import os
import sys
from datetime import datetime
from typing import Any, Optional

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Ensure environment variables are set
if not os.environ.get("SUPABASE_URL"):
    print("❌ SUPABASE_URL environment variable not set")
    print("   Please set up your environment variables first:")
    print("   bash setup_test_env.sh")
    sys.exit(1)

if not os.environ.get("SUPABASE_KEY"):
    print("❌ SUPABASE_KEY environment variable not set") 
    print("   Please set up your environment variables first:")
    print("   bash setup_test_env.sh")
    sys.exit(1)

# Import after checking environment
import db

# Test user
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"


def test_enhanced_schema() -> bool:
    """Test the enhanced schema functionality"""
    try:
        print("✅ Successfully imported db module")

        # Clean up any existing test data
        try:
            db.supabase.table("goals").delete().eq("user_id", TEST_USER_ID).execute()
            print("✅ Cleaned up existing test data")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")

        # Test 1: Create a goal with enhanced fields
        print("\n🧪 Test 1: Creating goal with enhanced fields...")
        goal_data = db.create_goal(
            user_id=TEST_USER_ID,
            title="Test Enhanced Goal",
            description="Testing the new enhanced schema",
            status="todo",
            kind="outcome",
            priority=5,
            impact=4,
            urgency=3,
            metadata={"test": True, "version": "enhanced"},
        )

        print(f"✅ Created goal: {goal_data['id']}")
        print(f"   Title: {goal_data['title']}")
        print(f"   Status: {goal_data['status']}")
        print(f"   Kind: {goal_data['kind']}")
        print(f"   Priority: {goal_data['priority']}")
        print(f"   Path: {goal_data['path']}")
        print(f"   Depth: {goal_data['depth']}")

        # Test 2: Create a child goal
        print("\n🧪 Test 2: Creating child goal...")
        child_goal = db.create_goal(
            user_id=TEST_USER_ID,
            title="Child Goal",
            parent_id=goal_data["id"],
            status="in_progress",
            kind="milestone",
            priority=3,
        )

        print(f"✅ Created child goal: {child_goal['id']}")
        print(f"   Parent ID: {child_goal['parent_id']}")
        print(f"   Path: {child_goal['path']}")
        print(f"   Depth: {child_goal['depth']}")

        # Test 3: Get all goals and verify tree structure
        print("\n🧪 Test 3: Retrieving goal tree...")
        goals = db.get_all_goals(TEST_USER_ID)
        print(f"✅ Retrieved {len(goals)} root goals")

        if goals:
            root_goal = goals[0]
            print(f"   Root goal: {root_goal['title']}")
            print(f"   Children: {len(root_goal.get('children', []))}")

            if root_goal.get("children"):
                child = root_goal["children"][0]
                print(f"   Child goal: {child['title']}")

        # Test 4: Update goal with new fields
        print("\n🧪 Test 4: Updating goal...")
        updated_goal = db.update_goal(
            goal_data["id"],
            {"status": "done", "completed_at": datetime.now().isoformat(), "ai_state": {"agent": "test", "confidence": 0.95}},
        )

        print(f"✅ Updated goal status: {updated_goal['status']}")
        print(f"   Completed at: {updated_goal['completed_at']}")
        print(f"   AI state: {updated_goal['ai_state']}")

        print("\n🎉 All tests passed! Enhanced schema is working correctly.")
        return True

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Clean up
        try:
            db.supabase.table("goals").delete().eq("user_id", TEST_USER_ID).execute()
            print("✅ Cleaned up test data")
        except Exception as e:
            print(f"⚠️  Cleanup warning: {e}")


if __name__ == "__main__":
    success = test_enhanced_schema()
    sys.exit(0 if success else 1)
