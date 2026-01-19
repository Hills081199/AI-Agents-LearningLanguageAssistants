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
    """Create or Update a study session (Activity Log). Stores only the latest score per activity."""
    try:
        user_id = str(current_user.id)
        
        # Prepare data for insertion/update
        data = session.model_dump(mode='json')
        data["user_id"] = user_id
        
        # Ensure start_time is updated to now
        from datetime import datetime
        data["start_time"] = datetime.now().isoformat()
        
        # Check if session exists for this lesson and activity type
        lesson_id = data.get("lesson_id")
        activity_type = data.get("activity_type")
        
        existing = None
        if lesson_id and activity_type:
             query = supabase.table("study_sessions")\
                .select("id")\
                .eq("user_id", user_id)\
                .eq("lesson_id", lesson_id)\
                .eq("activity_type", activity_type)\
                .execute()
             if query.data and len(query.data) > 0:
                 existing = query.data[0]

        if existing:
            # Update existing session
            session_id = existing['id']
            # We don't need to specify ID in data for update, just usage in EQ
            response = supabase.table("study_sessions").update(data).eq("id", session_id).execute()
        else:
            # Insert new session
            response = supabase.table("study_sessions").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to save session")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error creating/updating session: {str(e)}")
        print(f"Data payload: {data}")
        raise HTTPException(status_code=500, detail=f"Error processing session: {str(e)}")


@router.get("/", response_model=List[StudySession])
def get_sessions(
    lesson_id: str = None,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all study sessions for the current user, optionally filtered by lesson_id."""
    try:
        user_id = str(current_user.id)
        
        query = supabase.table("study_sessions").select("*").eq("user_id", user_id)
        
        if lesson_id:
            query = query.eq("lesson_id", lesson_id)
            
        response = query.order("start_time", desc=True).execute()
        
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
