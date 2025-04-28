from fastapi import FastAPI, HTTPException, Depends, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from uuid import uuid4, UUID
from typing import List, Optional, Dict, Any
import os
from dotenv import load_dotenv
from api import db
from jose import jwt
import logging
import time

# Load environment variables
load_dotenv()

# Configure auth
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-for-development")
AUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")
print(f"[DEBUG] JWT_SECRET={JWT_SECRET}")

app = FastAPI(
    title="GPT GoalGraph API",
    description="Minimal API for managing hierarchical goals, designed for GPT native tool-calling.",
    version="0.1.0",
)

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("FRONTEND_URL", "*")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Goal(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    title: str
    status: str = Field(default="todo", pattern="^(todo|doing|done)$")
    children: List["Goal"] = []

    class Config:
        json_schema_extra = {
            "example": {
                "id": "9b2b1ef8-95c8-4b8e-9f4a-2f1921d1fb3e",
                "title": "Buy GPUs",
                "status": "todo",
                "children": [],
            }
        }

Goal.update_forward_refs()

class GoalCreate(BaseModel):
    title: str
    parent_id: Optional[UUID] = None

class GoalUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[str] = Field(default=None, pattern="^(todo|doing|done)$")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> Dict[str, Any]:
    """
    Verify JWT token and extract user info.
    """
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"], audience=AUDIENCE)
        # Warn if token is about to expire within 5 minutes
        exp = payload.get("exp")
        if exp:
            now = int(time.time())
            if exp - now <= 300:
                logging.warning(f"JWT expiring soon (in {exp - now} seconds)")
        
        # Alternatively, validate with Supabase directly
        # user = db.supabase.auth.api.get_user(token)
        
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid authentication: {str(e)}")

@app.get("/goals")
async def list_goals(user: Dict[str, Any] = Depends(get_current_user)):
    """Return entire goal tree for the authenticated user"""
    user_id = user.get("sub")  # JWT standard claim for user ID
    goals = db.get_all_goals(user_id)
    return goals
 
@app.get("/goals/{goal_id}")
async def get_goal(goal_id: UUID, user: Dict[str, Any] = Depends(get_current_user)):
    """Get a single goal with nested children for the authenticated user"""
    user_id = user.get("sub")
    goals = db.get_all_goals(user_id)
    # Recursive search for the requested goal
    def _find(nodes: List[Dict[str, Any]], target_id: str) -> Optional[Dict[str, Any]]:
        for node in nodes:
            if str(node.get("id")) == target_id:
                return node
            child = _find(node.get("children", []), target_id)
            if child:
                return child
        return None
    result = _find(goals, str(goal_id))
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found")
    return result

@app.post("/goals", status_code=201)
async def create_goal(payload: GoalCreate, user: Dict[str, Any] = Depends(get_current_user)):
    """Create a new goal for the authenticated user"""
    user_id = user.get("sub")
    parent_id = str(payload.parent_id) if payload.parent_id else None
    goal = db.create_goal(user_id, payload.title, parent_id)
    return goal

@app.patch("/goals/{goal_id}")
async def update_goal(goal_id: UUID, payload: GoalUpdate, user: Dict[str, Any] = Depends(get_current_user)):
    """Update a goal's properties"""
    updates = {}
    if payload.title is not None:
        updates["title"] = payload.title
    if payload.status is not None:
        updates["status"] = payload.status
        
    goal = db.update_goal(str(goal_id), updates)
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    return goal

@app.delete("/goals/{goal_id}", status_code=204)
async def delete_goal(goal_id: UUID, user: Dict[str, Any] = Depends(get_current_user)):
    """Delete a goal"""
    success = db.delete_goal(str(goal_id))
    if not success:
        raise HTTPException(status_code=404, detail="Goal not found")
    return None

# Root endpoint for health checks
@app.get("/")
async def root():
    return {"status": "ok", "message": "GPT GoalGraph API is running"}

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
    return goals