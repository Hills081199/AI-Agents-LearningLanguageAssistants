import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from supabase import Client
from database import get_supabase
from dependencies import get_current_user
from models import LessonHistory, LessonHistoryCreate, LessonHistoryUpdate

router = APIRouter(
    prefix="/lesson-history",
    tags=["Lesson History"],
    responses={404: {"description": "Not found"}},
)


@router.post("/", response_model=LessonHistory, status_code=status.HTTP_201_CREATED)
def create_lesson_history(
    history: LessonHistoryCreate,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Save a lesson to history."""
    try:
        user_id = str(current_user.id)
        
        # Prepare data
        data = history.model_dump()
        data["user_id"] = user_id
        if "language" in data and data["language"]:
            data["language"] = data["language"].lower()
        
        
        # Insert into Supabase
        response = supabase.table("lesson_history").insert(data).execute()
        
        if not response.data:
            raise HTTPException(status_code=500, detail="Failed to save lesson history")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[LessonHistory])
def get_all_lesson_history(
    language: Optional[str] = None,
    level: Optional[str] = None,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get all lesson history for the current user with optional filters."""
    try:
        user_id = str(current_user.id)
        
        query = supabase.table("lesson_history").select("*").eq("user_id", user_id)
        
        # Apply filters if provided
        if language:
            query = query.eq("language", language.lower())
        if level:
            query = query.eq("level", level)
        
        response = query.order("created_at", desc=True).execute()
        
        return response.data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{history_id}", response_model=LessonHistory)
def get_lesson_history(
    history_id: str,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get a specific lesson history by ID."""
    try:
        user_id = str(current_user.id)
        
        response = supabase.table("lesson_history").select("*").eq("id", history_id).eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(status_code=404, detail="Lesson history not found")
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{history_id}", response_model=LessonHistory)
def update_lesson_history(
    history_id: str,
    history_update: LessonHistoryUpdate,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Update a lesson history entry (e.g., update scores)."""
    try:
        user_id = str(current_user.id)
        
        # Check if history exists and belongs to user
        existing = supabase.table("lesson_history").select("id").eq("id", history_id).eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Lesson history not found")
        
        # Update only provided fields
        update_data = history_update.model_dump(exclude_unset=True)
        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        response = supabase.table("lesson_history").update(update_data).eq("id", history_id).eq("user_id", user_id).execute()
        
        return response.data[0]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{history_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_lesson_history(
    history_id: str,
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Delete a lesson history entry."""
    try:
        user_id = str(current_user.id)
        
        # Check if history exists and belongs to user
        existing = supabase.table("lesson_history").select("id").eq("id", history_id).eq("user_id", user_id).execute()
        if not existing.data:
            raise HTTPException(status_code=404, detail="Lesson history not found")
        
        supabase.table("lesson_history").delete().eq("id", history_id).eq("user_id", user_id).execute()
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats/summary")
def get_learning_stats(
    current_user = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """Get learning statistics summary for the current user."""
    try:
        user_id = str(current_user.id)
        
        # Get all history
        response = supabase.table("lesson_history").select("*").eq("user_id", user_id).execute()
        
        history = response.data or []
        
        # Calculate stats
        total_lessons = len(history)
        
        # Group by language
        languages = {}
        for lesson in history:
            lang = lesson.get("language", "chinese")
            if lang not in languages:
                languages[lang] = {"count": 0, "quiz_avg": 0, "writing_avg": 0}
            languages[lang]["count"] += 1
            if lesson.get("quiz_score"):
                languages[lang]["quiz_avg"] += lesson["quiz_score"]
            if lesson.get("writing_score"):
                languages[lang]["writing_avg"] += lesson["writing_score"]
        
        # Calculate averages
        for lang in languages:
            count = languages[lang]["count"]
            if count > 0:
                languages[lang]["quiz_avg"] = round(languages[lang]["quiz_avg"] / count, 1)
                languages[lang]["writing_avg"] = round(languages[lang]["writing_avg"] / count, 1)
        
        return {
            "total_lessons": total_lessons,
            "by_language": languages
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
