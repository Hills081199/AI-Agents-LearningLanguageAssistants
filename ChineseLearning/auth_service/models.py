from pydantic import BaseModel, UUID4
from typing import Optional, List, Dict, Any
from datetime import datetime


# ============== Auth Models ==============

class SignUpRequest(BaseModel):
    email: str
    password: str
    username: Optional[str] = None

class SignInRequest(BaseModel):
    email: str
    password: str

class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]

class UserProfile(BaseModel):
    id: str
    email: Optional[str] = None
    username: Optional[str] = None


# ============== Study Session Models ==============

class StudySessionBase(BaseModel):
    topic: str
    level: str
    language: str = "chinese"

class StudySessionCreate(StudySessionBase):
    pass

class StudySessionUpdate(BaseModel):
    topic: Optional[str] = None
    level: Optional[str] = None
    language: Optional[str] = None
    end_time: Optional[datetime] = None

class StudySession(StudySessionBase):
    id: str
    user_id: str
    start_time: datetime
    end_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============== Lesson History Models ==============

class LessonHistoryBase(BaseModel):
    session_id: Optional[str] = None
    topic: str
    level: str
    language: str = "chinese"
    lesson_content: Dict[str, Any]
    quiz_score: Optional[int] = None
    writing_score: Optional[int] = None

class LessonHistoryCreate(LessonHistoryBase):
    pass

class LessonHistoryUpdate(BaseModel):
    quiz_score: Optional[int] = None
    writing_score: Optional[int] = None
    lesson_content: Optional[Dict[str, Any]] = None

class LessonHistory(LessonHistoryBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True
