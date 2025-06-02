import datetime
import logging
import os
import time
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import jwt
from pydantic import BaseModel, ConfigDict, Field

# Import db module - handle different import contexts
try:
    from . import db  # Package import
except ImportError:
    import db  # Direct import when running as script

# Load environment variables
load_dotenv()

# Configure auth
security = HTTPBearer()
JWT_SECRET = os.getenv("JWT_SECRET", "your-secret-key-for-development")
AUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")
print(f"[DEBUG] JWT_SECRET={JWT_SECRET}")
AUDIENCE = os.getenv("JWT_AUDIENCE", "authenticated")

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


class GoalStatus(str, Enum):
    todo = "todo"
    in_progress = "in_progress"
    blocked = "blocked"
    done = "done"


class IntentKind(str, Enum):
    outcome = "outcome"
    process = "process"
    habit = "habit"
    milestone = "milestone"


class Goal(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": "9b2b1ef8-95c8-4b8e-9f4a-2f1921d1fb3e",
                "title": "Buy GPUs",
                "description": "Acquire hardware for AI training",
                "status": "todo",
                "kind": "outcome",
                "priority": 5,
                "impact": 4,
                "urgency": 3,
                "children": [],
            }
        }
    )

    id: UUID = Field(default_factory=uuid4)
    user_id: UUID
    title: str
    description: Optional[str] = None
    status: GoalStatus = GoalStatus.todo
    kind: IntentKind = IntentKind.outcome
    priority: int = Field(default=3, ge=1, le=5)
    impact: int = Field(default=3, ge=1, le=5)
    urgency: int = Field(default=3, ge=1, le=5)
    parent_id: Optional[UUID] = None
    path: Optional[str] = None  # ltree path as string
    depth: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    ai_state: Dict[str, Any] = Field(default_factory=dict)
    deadline: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime
    children: List["Goal"] = []


Goal.model_rebuild()


class GoalCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")  # Reject extra fields
    title: str
    description: Optional[str] = None
    status: Optional[GoalStatus] = GoalStatus.todo
    kind: Optional[IntentKind] = IntentKind.outcome
    priority: Optional[int] = Field(default=3, ge=1, le=5)
    impact: Optional[int] = Field(default=3, ge=1, le=5)
    urgency: Optional[int] = Field(default=3, ge=1, le=5)
    parent_id: Optional[UUID] = None
    deadline: Optional[datetime.datetime] = None
    metadata: Optional[Dict[str, Any]] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[GoalStatus] = None
    kind: Optional[IntentKind] = None
    priority: Optional[int] = Field(default=None, ge=1, le=5)
    impact: Optional[int] = Field(default=None, ge=1, le=5)
    urgency: Optional[int] = Field(default=None, ge=1, le=5)
    parent_id: Optional[UUID] = None
    deadline: Optional[datetime.datetime] = None
    completed_at: Optional[datetime.datetime] = None
    metadata: Optional[Dict[str, Any]] = None
    ai_state: Optional[Dict[str, Any]] = None


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
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    goals = db.get_all_goals(user_id)
    return goals


@app.get("/goals/{goal_id}")
async def get_goal(goal_id: UUID, user: Dict[str, Any] = Depends(get_current_user)):
    """Get a single goal with nested children for the authenticated user"""
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
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
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")

    try:
        parent_id = str(payload.parent_id) if payload.parent_id else None

        # Prepare kwargs for optional fields
        kwargs = {}
        field_mappings = [
            ("description", payload.description),
            ("status", payload.status.value if payload.status else None),
            ("kind", payload.kind.value if payload.kind else None),
            ("priority", payload.priority),
            ("impact", payload.impact),
            ("urgency", payload.urgency),
            ("deadline", payload.deadline),
            ("metadata", payload.metadata),
        ]

        for field_name, field_value in field_mappings:
            if field_value is not None:
                kwargs[field_name] = field_value

        goal = db.create_goal(user_id, payload.title, parent_id, **kwargs)
        return goal
    except Exception as e:
        # Convert database errors to appropriate HTTP responses
        error_msg = str(e).lower()
        if "constraint" in error_msg or "violation" in error_msg:
            raise HTTPException(status_code=400, detail="Invalid data or constraint violation")
        elif "timeout" in error_msg or "network" in error_msg:
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@app.patch("/goals/{goal_id}")
async def update_goal(goal_id: UUID, payload: GoalUpdate, user: Dict[str, Any] = Depends(get_current_user)):
    """Update a goal's properties"""
    try:
        updates = {}
        
        # Map payload fields to updates dictionary
        field_mappings = [
            ("title", payload.title),
            ("description", payload.description),
            ("status", payload.status.value if payload.status else None),
            ("kind", payload.kind.value if payload.kind else None),
            ("priority", payload.priority),
            ("impact", payload.impact),
            ("urgency", payload.urgency),
            ("parent_id", str(payload.parent_id) if payload.parent_id else None),
            ("deadline", payload.deadline),
            ("completed_at", payload.completed_at),
            ("metadata", payload.metadata),
            ("ai_state", payload.ai_state),
        ]

        for field_name, field_value in field_mappings:
            if field_value is not None:
                updates[field_name] = field_value

        goal = db.update_goal(str(goal_id), updates)
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        return goal
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception as e:
        # Convert database errors to appropriate HTTP responses
        error_msg = str(e).lower()
        if "timeout" in error_msg or "network" in error_msg:
            raise HTTPException(status_code=503, detail="Service temporarily unavailable")
        else:
            raise HTTPException(status_code=500, detail="Internal server error")


@app.delete("/goals/{goal_id}", status_code=204)
async def delete_goal(goal_id: UUID, user: Dict[str, Any] = Depends(get_current_user)):
    """Delete a goal"""
    try:
        success = db.delete_goal(str(goal_id))
        if not success:
            raise HTTPException(status_code=404, detail="Goal not found")
        return None
    except HTTPException:
        raise  # Re-raise HTTP exceptions as-is
    except Exception:
        # Convert database errors to appropriate HTTP responses
        raise HTTPException(status_code=500, detail="Internal server error")


# JSON export endpoint for the tree visualization
@app.get("/api/tree", response_model=TreeResponse)
async def get_tree(user: Dict[str, Any] = Depends(get_current_user)):
    """
    Return the goal tree in a format optimized for frontend visualization.

    Returns:
        A TreeResponse object with all nodes in a flat array and metadata
    """
    user_id = user.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="User ID not found in token")
    raw_goals = db.get_all_goals(user_id)

    # Convert the hierarchical structure to flat nodes array
    nodes = []

    def _flatten_tree(goal_list, parent_id=None):
        for goal in goal_list:
            # Map status from backend to frontend format
            status_map = {"todo": "pending", "doing": "active", "done": "done"}

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
                "ui": {"collapsed": False},
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
        "nodes": nodes,
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
    if not user_id:
        raise HTTPException(status_code=500, detail="DEFAULT_USER_ID environment variable not configured")
    goals = db.get_all_goals(user_id)
    return goals


# Root endpoint for health checks
@app.get("/")
async def root():
    return {"status": "ok", "message": "GPT GoalGraph API is running"}
