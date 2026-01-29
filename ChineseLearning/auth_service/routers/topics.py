from fastapi import APIRouter, Depends, HTTPException
from supabase import Client
from database import get_supabase
from dependencies import get_current_user
from pydantic import BaseModel
from typing import Optional
import random

router = APIRouter(prefix="/topics", tags=["topics"])

class TopicSuggestionRequest(BaseModel):
    level: str
    language: str = "chinese"

@router.post("/suggest-db")
def suggest_topic_from_db(
    request: TopicSuggestionRequest,
    user=Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Suggest a topic from the 'topics' table that the user has NOT yet learned.
    Returns {topic: str} or {topic: None} if no topics available.
    """
    try:
        user_id = user.id
        
        # 1. Get topics already learned by the user
        # Note: In a real prod environment with many records, this should be done via a Joined View or RPC for performance.
        history_res = supabase.table("lesson_history").select("topic").eq("user_id", user_id).execute()
        learned_topics = set(item['topic'] for item in history_res.data)
        
        # 2. Get all candidate topics for this level/language from 'topics' table
        topics_res = supabase.table("topics").select("name").eq("level", request.level).eq("language", request.language).execute()
        candidate_topics = [item['name'] for item in topics_res.data]
        
        # 3. Filter out learned topics
        available_topics = [t for t in candidate_topics if t not in learned_topics]
        
        if not available_topics:
            return {"topic": None}
        
        # 4. Pick a random topic
        selected_topic = random.choice(available_topics)
        
        return {"topic": selected_topic}
    except Exception as e:
        print(f"Error in suggest_topic_from_db: {e}")
        raise HTTPException(status_code=500, detail=str(e))
