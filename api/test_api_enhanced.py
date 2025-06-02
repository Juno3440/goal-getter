#!/usr/bin/env python3
"""
Simple HTTP test for the enhanced API endpoints
"""

import json
import os
import sys
from datetime import datetime

import requests

# Set up dev environment
os.environ["SUPABASE_URL"] = "https://tstnyxldiqfbcvzxtzxi.supabase.co"
os.environ["SUPABASE_KEY"] = (
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InRzdG55eGxkaXFmYmN2enh0enhpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NDg4ODY5MTgsImV4cCI6MjA2NDQ2MjkxOH0.qinSNo9vUvAEQsrJcESBjmUnJWagJbSX0RguxjMr1C0"
)

# Test configuration
API_BASE = "http://localhost:8000"
TEST_USER_ID = "550e8400-e29b-41d4-a716-446655440000"

# Create a test JWT token
import jwt as jose_jwt

JWT_SECRET = "your-secret-key-for-development"

test_token = jose_jwt.encode(
    {
        "sub": TEST_USER_ID,
        "aud": "authenticated",
        "exp": int(datetime.now().timestamp()) + 3600,  # 1 hour from now
        "iat": int(datetime.now().timestamp()),
    },
    JWT_SECRET,
    algorithm="HS256",
)

headers = {"Authorization": f"Bearer {test_token}", "Content-Type": "application/json"}


def test_enhanced_api():
    """Test the enhanced API endpoints"""
    try:
        print("🧪 Testing Enhanced API Endpoints")
        print(f"API Base: {API_BASE}")
        print(f"Test User: {TEST_USER_ID}")

        # Test 1: Create a goal with enhanced fields
        print("\n📝 Test 1: Creating goal with enhanced fields...")
        goal_data = {
            "title": "Enhanced API Test Goal",
            "description": "Testing the enhanced API with all new fields",
            "status": "todo",
            "kind": "outcome",
            "priority": 5,
            "impact": 4,
            "urgency": 3,
            "metadata": {"test": True, "api_version": "enhanced"},
        }

        response = requests.post(f"{API_BASE}/goals", json=goal_data, headers=headers)
        if response.status_code == 201:
            created_goal = response.json()
            print(f"✅ Created goal: {created_goal['id']}")
            print(f"   Title: {created_goal['title']}")
            print(f"   Status: {created_goal['status']}")
            print(f"   Kind: {created_goal['kind']}")
            print(f"   Priority: {created_goal['priority']}")
            print(f"   Path: {created_goal.get('path', 'N/A')}")
            goal_id = created_goal["id"]
        else:
            print(f"❌ Failed to create goal: {response.status_code} - {response.text}")
            return False

        # Test 2: Get the goal
        print("\n📖 Test 2: Retrieving goal...")
        response = requests.get(f"{API_BASE}/goals/{goal_id}", headers=headers)
        if response.status_code == 200:
            retrieved_goal = response.json()
            print(f"✅ Retrieved goal: {retrieved_goal['title']}")
        else:
            print(f"❌ Failed to retrieve goal: {response.status_code} - {response.text}")
            return False

        # Test 3: Update the goal
        print("\n✏️  Test 3: Updating goal...")
        update_data = {
            "status": "done",
            "completed_at": datetime.now().isoformat(),
            "ai_state": {"agent": "api_test", "confidence": 0.95},
        }

        response = requests.patch(f"{API_BASE}/goals/{goal_id}", json=update_data, headers=headers)
        if response.status_code == 200:
            updated_goal = response.json()
            print(f"✅ Updated goal status: {updated_goal['status']}")
            print(f"   AI state: {updated_goal.get('ai_state', 'N/A')}")
        else:
            print(f"❌ Failed to update goal: {response.status_code} - {response.text}")
            return False

        # Test 4: List all goals
        print("\n📋 Test 4: Listing all goals...")
        response = requests.get(f"{API_BASE}/goals", headers=headers)
        if response.status_code == 200:
            goals = response.json()
            print(f"✅ Retrieved {len(goals)} goals")
        else:
            print(f"❌ Failed to list goals: {response.status_code} - {response.text}")
            return False

        # Test 5: Delete the goal
        print("\n🗑️  Test 5: Deleting goal...")
        response = requests.delete(f"{API_BASE}/goals/{goal_id}", headers=headers)
        if response.status_code == 204:
            print("✅ Successfully deleted goal")
        else:
            print(f"❌ Failed to delete goal: {response.status_code} - {response.text}")
            return False

        print("\n🎉 All API tests passed! Enhanced schema is working correctly.")
        return True

    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("⚠️  Make sure the FastAPI server is running on localhost:8000")
    print("   Run: uvicorn main:app --reload")
    print()

    success = test_enhanced_api()
    sys.exit(0 if success else 1)
