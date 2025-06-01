import os, time, logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from supabase import create_client
from jose import jwt              # python-jose

# Load environment variables
load_dotenv()

url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

if not url or not key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables are required")

supabase = create_client(url, key)
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")   # <-- NEW
# Debug: print environment values (masking key) and ping DB
_masked_key = (key[:8] + "*" * (len(key) - 8)) if key else ""
print(f"[DEBUG] SUPABASE_URL={url}")
print(f"[DEBUG] SUPABASE_KEY={_masked_key}")
try:
    _ping = supabase.table("goals").select("id").limit(1).execute()
    print(f"[DEBUG] DB PING result: {_ping.data}")
except Exception as _e:
    print(f"[DEBUG] DB PING error: {_e}")
    
def verify_token(token: str) -> Dict[str, Any]:
    """
    Decode and validate a Supabase JWT.
    Warns if the token expires within 5 minutes.
    """
    payload = jwt.decode(
        token,
        key,
        algorithms=["HS256"],
        audience=JWT_AUDIENCE
    )

    exp = payload.get("exp", 0)
    ttl = exp - time.time()
    if ttl <= 300:
        logging.warning(f"JWT expires in {int(ttl)} s")
    return payload


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
    
    for r in by_id.values():
        pid = r.get("parent_id")
        if pid and str(pid) in by_id:
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