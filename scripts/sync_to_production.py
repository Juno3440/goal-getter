#!/usr/bin/env python3
"""
Sync script to copy /app/ to /api/ and add production-specific features.

This maintains /app/ as the source of truth for development while ensuring
/api/ has all production features needed for deployment.
"""

import os
import shutil
import filecmp
from pathlib import Path

def main():
    """Main sync function."""
    project_root = Path(__file__).parent.parent
    app_dir = project_root / "app"
    api_dir = project_root / "api"
    
    print("🔄 Syncing /app/ to /api/ for production deployment...")
    
    # Step 1: Copy base files from /app/ to /api/
    print("📋 Copying base files...")
    
    # Copy requirements.txt
    shutil.copy2(app_dir / "requirements.txt", api_dir / "requirements.txt")
    print("  ✅ requirements.txt")
    
    # Copy __init__.py if it exists in /app/, otherwise create an empty one
    app_init = app_dir / "__init__.py"
    api_init = api_dir / "__init__.py"
    if app_init.exists():
        shutil.copy2(app_init, api_init)
        print("  ✅ __init__.py (copied)")
    else:
        # Create empty __init__.py if it doesn't exist
        api_init.touch()
        print("  ✅ __init__.py (created empty)")
    
    # Step 2: Sync db.py with production enhancements
    print("📋 Syncing db.py with production features...")
    sync_db_file(app_dir, api_dir)
    
    # Step 3: Sync main.py with production enhancements
    print("📋 Syncing main.py with production features...")
    sync_main_file(app_dir, api_dir)
    
    print("✅ Sync completed successfully!")
    print("🚀 /api/ is now ready for production deployment")

def sync_db_file(app_dir: Path, api_dir: Path):
    """Sync db.py from /app/ to /api/ with production enhancements."""
    app_db = app_dir / "db.py"
    api_db = api_dir / "db.py"
    
    # Read the clean development version
    with open(app_db, 'r') as f:
        content = f.read()
    
    # Add production-specific imports
    production_imports = """import os, time, logging
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv
from supabase import create_client
from jose import jwt              # python-jose"""
    
    # Replace the import section
    lines = content.split('\n')
    import_end = 0
    for i, line in enumerate(lines):
        if line.startswith('from dotenv import load_dotenv'):
            import_end = i + 1
            break
    
    # Rebuild with production imports
    new_lines = production_imports.split('\n') + lines[import_end:]
    
    # Add production-specific features after supabase client creation
    client_creation_index = None
    for i, line in enumerate(new_lines):
        if 'supabase = create_client(url, key)' in line:
            client_creation_index = i
            break
    
    if client_creation_index:
        # Insert production debugging and JWT audience
        production_features = [
            'JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")   # <-- NEW',
            '# Debug: print environment values (masking key) and ping DB',
            '_masked_key = (key[:8] + "*" * (len(key) - 8)) if key else ""',
            'print(f"[DEBUG] SUPABASE_URL={url}")',
            'print(f"[DEBUG] SUPABASE_KEY={_masked_key}")',
            'try:',
            '    _ping = supabase.table("goals").select("id").limit(1).execute()',
            '    print(f"[DEBUG] DB PING result: {_ping.data}")',
            'except Exception as _e:',
            '    print(f"[DEBUG] DB PING error: {_e}")',
            '    ',
            'def verify_token(token: str) -> Dict[str, Any]:',
            '    """',
            '    Decode and validate a Supabase JWT.',
            '    Warns if the token expires within 5 minutes.',
            '    """',
            '    payload = jwt.decode(',
            '        token,',
            '        key,',
            '        algorithms=["HS256"],',
            '        audience=JWT_AUDIENCE',
            '    )',
            '',
            '    exp = payload.get("exp", 0)',
            '    ttl = exp - time.time()',
            '    if ttl <= 300:',
            '        logging.warning(f"JWT expires in {int(ttl)} s")',
            '    return payload',
            ''
        ]
        
        new_lines[client_creation_index+1:client_creation_index+1] = production_features
    
    # Write the enhanced version
    with open(api_db, 'w') as f:
        f.write('\n'.join(new_lines))
    
    print("  ✅ db.py enhanced with production features")

def sync_main_file(app_dir: Path, api_dir: Path):
    """Sync main.py from /app/ to /api/ with production enhancements."""
    app_main = app_dir / "main.py"
    api_main = api_dir / "main.py"
    
    # Read the clean development version
    with open(app_main, 'r') as f:
        content = f.read()
    
    # Add production-specific features
    production_additions = {
        # Add debug print for JWT_SECRET
        'JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-for-development")': 
        'JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-for-development")\nAUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")\nprint(f"[DEBUG] JWT_SECRET={JWT_SECRET}")',
        
        # Add TreeNode and TreeResponse models
        'class GoalUpdate(BaseModel):': '''class GoalUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(todo|doing|done)$")

class TreeNode(BaseModel):
    id: str
    parent_id: Optional[str] = None
    title: str
    progress: float = 0.0
    status: str = "pending"
    style: Dict[str, str] = Field(default_factory=lambda: {"color": "#1f2937", "accent": "#3b82f6"})
    ui: Dict[str, bool] = Field(default_factory=lambda: {"collapsed": False})

class TreeResponse(BaseModel):
    schema_version: str = "1.0.0"
    generated_at: str
    root_id: Optional[str] = None
    nodes: List[TreeNode]

class GoalUpdate(BaseModel):'''
    }
    
    # Apply replacements
    for old, new in production_additions.items():
        content = content.replace(old, new)
    
    # Add the /api/tree endpoint if it doesn't exist
    if '/api/tree' not in content:
        tree_endpoint = '''
# JSON export endpoint for the tree visualization
@app.get("/api/tree", response_model=TreeResponse)
async def get_tree(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Return the goal tree in a format optimized for frontend visualization.
    
    Returns:
        A TreeResponse object with all nodes in a flat array and metadata
    """
    user_id = user.get("sub")
    raw_goals = db.get_all_goals(user_id)
    
    # Convert the hierarchical structure to flat nodes array
    nodes = []
    
    def _flatten_tree(goal_list, parent_id=None):
        for goal in goal_list:
            # Map status from backend to frontend format
            status_map = {
                "todo": "pending",
                "doing": "active",
                "done": "done"
            }
            
            # Calculate progress based on children
            progress = 0.0
            if goal.get("status") == "done":
                progress = 1.0
            elif goal.get("status") == "doing":
                progress = 0.5
            
            # Create TreeNode
            node = {
                "id": goal.get("id"),
                "parent_id": parent_id,
                "title": goal.get("title"),
                "progress": progress,
                "status": status_map.get(goal.get("status"), "pending"),
                "style": {"color": "#1f2937", "accent": "#3b82f6"},
                "ui": {"collapsed": False}
            }
            
            nodes.append(node)
            
            # Process children
            if goal.get("children"):
                _flatten_tree(goal.get("children"), goal.get("id"))
    
    # Start with root goals (those without parent)
    _flatten_tree(raw_goals)
    
    # Find a root node if available
    root_id = None
    if nodes:
        # Use the first node without a parent as the root
        for node in nodes:
            if node["parent_id"] is None:
                root_id = node["id"]
                break
    
    return {
        "schema_version": "1.0.0",
        "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "root_id": root_id,
        "nodes": nodes
    }

# GPT integration helper - for minimal API key auth
@app.get("/gpt/goals", include_in_schema=False)
async def gpt_list_goals(api_key: Optional[str] = Header(None)):
    """Simplified endpoint for GPT to access goals without full JWT auth"""
    # Very basic API key validation
    if api_key != os.getenv("GPT_API_KEY"):
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Get user ID from API key mapping (or use a default during development)
    user_id = os.getenv("DEFAULT_USER_ID")
    goals = db.get_all_goals(user_id)
    return goals'''
        
        # Insert before the last line (or after the root endpoint)
        if '# Root endpoint for health checks' in content:
            content = content.replace('# Root endpoint for health checks', tree_endpoint + '\n\n# Root endpoint for health checks')
        else:
            content += tree_endpoint
    
    # Add required datetime import
    if 'import datetime' not in content:
        content = content.replace('import os', 'import os\nimport datetime')
    
    # Write the enhanced version
    with open(api_main, 'w') as f:
        f.write(content)
    
    print("  ✅ main.py enhanced with production features")

if __name__ == "__main__":
    main()