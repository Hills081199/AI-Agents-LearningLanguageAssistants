import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from supabase import Client
from database import get_supabase
from dependencies import get_current_user
from models import StudySession, StudySessionCreate, StudySessionUpdate

router = APIRouter(
    prefix="/sessions",
    tags=["Study Sessions"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=StudySession, status_code=status.HTTP_201_CREATED)
def create_session(
    session: StudySessionCreate,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Create a new study session."""
    try:
        user_id = str(current_user.id)
        
        # Prepare data for insertion
        data = session.model_dump()
        data["user_id"] = user_id
        
        # Insert into Supabase
        response = supabase.table("study_sessions").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to create session")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[StudySession])
def get_sessions(
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all study sessions for the current user."""
    try:
        user_id = str(current_user.id)
        
        response = supabase.table("study_sessions").select("*").eq("user_id", user_id).order("start_time", desc=True).execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{session_id}", response_model=StudySession)
def get_session(
    session_id: str,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get a specific study session by ID."""
    try:
        user_id = str(current_user.id)
        
        response = supabase.table("study_sessions").select("*").eq("id", session_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{session_id}", response_model=StudySession)
def update_session(
    session_id: str,
    session_update: StudySessionUpdate,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update a study session."""
    try:
        user_id = str(current_user.id)
        
        # Check if session exists and belongs to user
        existing = supabase.table("study_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Update only provided fields
        update_data = session_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("study_sessions").update(update_data).eq("id", session_id).eq("user_id", user_id).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_session(
    session_id: str,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete a study session."""
    try:
        user_id = str(current_user.id)
        
        # Check if session exists and belongs to user
        existing = supabase.table("study_sessions").select("id").eq("id", session_id).eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Session not found")
        
        supabase.table("study_sessions").delete().eq("id", session_id).eq("user_id", user_id).execute()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
