from supabase import create_client
from typing import Dict, List, Any, Optional
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

supabase = create_client(url, key)

def build_tree(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Convert flat table rows to a hierarchical tree.
    
    Args:
        rows: List of flat goal rows from the database
        
    Returns:
        List of root-level goals with nested children
    """
    by_id = {str(r["id"]): {**r, "children": []} for r in rows}
    root = []
    
    # Track nodes that are part of circular references
    visited = set()
    in_cycle = set()
    
    def detect_cycle(node_id: str, path: set) -> bool:
        """Detect if a node is part of a circular reference."""
        if node_id in path:
            return True
        if node_id in visited:
            return False
        
        visited.add(node_id)
        path.add(node_id)
        
        node = by_id.get(node_id)
        if node:
            parent_id = node.get("parent_id")
            if parent_id and str(parent_id) in by_id:
                if detect_cycle(str(parent_id), path):
                    in_cycle.add(node_id)
                    return True
        
        path.remove(node_id)
        return False
    
    # Detect all circular references
    for node_id in by_id:
        if node_id not in visited:
            detect_cycle(node_id, set())
    
    # Build the tree, treating circular nodes as roots
    for r in by_id.values():
        pid = r.get("parent_id")
        node_id = str(r["id"])
        
        # If this node is part of a cycle, treat it as a root
        if node_id in in_cycle:
            root.append(r)
        elif pid and str(pid) in by_id and str(pid) not in in_cycle:
            by_id[str(pid)]["children"].append(r)
        else:
            root.append(r)
            
    return root

def get_all_goals(user_id: str) -> List[Dict[str, Any]]:
    """
    Fetch all goals for a user and build the goal tree.
    
    Args:
        user_id: The authenticated user's ID
        
    Returns:
        Hierarchical tree of user's goals
    """
    data = supabase \
        .table("goals") \
        .select("*") \
        .eq("user_id", user_id) \
        .execute()
    
    return build_tree(data.data)

def create_goal(user_id: str, title: str, parent_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a new goal for the user.
    
    Args:
        user_id: The authenticated user's ID
        title: The goal title
        parent_id: Optional parent goal ID
        
    Returns:
        The created goal data
    """
    payload = {
        "user_id": user_id,
        "title": title
    }
    
    if parent_id:
        payload["parent_id"] = parent_id
    
    response = supabase.table("goals").insert(payload).execute()
    return response.data[0] if response.data else {}

def update_goal(goal_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Update a goal's properties.
    
    Args:
        goal_id: The goal ID to update
        updates: Dictionary of fields to update (title, status)
        
    Returns:
        Updated goal data
    """
    updates["updated_at"] = "NOW()"
    response = supabase.table("goals") \
        .update(updates) \
        .eq("id", goal_id) \
        .execute()
    
    return response.data[0] if response.data else {}

def delete_goal(goal_id: str) -> bool:
    """
    Delete a goal.
    
    Args:
        goal_id: The goal ID to delete
        
    Returns:
        True if successful, False otherwise
    """
    response = supabase.table("goals") \
        .delete() \
        .eq("id", goal_id) \
        .execute()
    
    return len(response.data) > 0