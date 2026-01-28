from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import os
import sys
import io
import os

# Force UTF-8 encoding for stdout/stderr to handle Chinese characters on Windows
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception:
    pass

import json
import time
from datetime import datetime

# Add parent directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from main import generate_lesson_content, get_topic_suggestion, generate_writing_prompt, grade_writing_submission
from agents import get_supported_languages, get_language_config


app = FastAPI(
    title="Language Learning Agent Service",
    description="AI Agent service for generating language lessons, quizzes, and writing assessments",
    version="1.0.0"
)

# CORS middleware - allow all origins for flexibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache for recently suggested topics to avoid repetitive results
recent_suggestions = {}


# ============== Request/Response Models ==============

class LessonRequest(BaseModel):
    topic: Optional[str] = None
    level: str = "HSK 5"
    language: str = "chinese"

class LessonResponse(BaseModel):
    topic: str
    level: str
    language: str
    lesson_plan: Optional[str] = None
    markdown_content: str
    html_content: str
    story: str
    vocabulary: List[Any] = []
    grammar: List[Any] = []
    quiz: List[Any] = []
    writing_prompt: Optional[Any] = None
    filename: Optional[str] = None

class TopicRequest(BaseModel):
    level: str = "HSK 3"
    language: str = "chinese"

class WritingPromptRequest(BaseModel):
    topic: str
    level: str = "HSK 5"
    language: str = "chinese"

class WritingGradeRequest(BaseModel):
    submission: str
    prompt: str  # JSON string of the prompt data
    language: str = "chinese"

class LanguageInfo(BaseModel):
    code: str
    name: str
    native_name: str
    levels: List[str]
    level_system: str


# ============== Language Endpoints ==============

@app.get("/languages", response_model=List[LanguageInfo])
def get_languages():
    """Get all supported languages with their level systems."""
    return get_supported_languages()

@app.get("/languages/{language_code}")
def get_language_details(language_code: str):
    """Get details for a specific language."""
    config = get_language_config(language_code)
    if not config:
        raise HTTPException(status_code=404, detail=f"Language '{language_code}' not found")
    return {
        "code": language_code,
        "name": config["name"],
        "native_name": config["native_name"],
        "levels": config["levels"],
        "level_system": config["level_system"],
        "tts_code": config["tts_code"],
        "has_romanization": config.get("has_romanization", False),
        "romanization_name": config.get("romanization_name", None)
    }


# ============== Lesson Generation Endpoints ==============

@app.post("/suggest-topic")
def suggest_topic(request: TopicRequest):
    """Suggest a random topic for the specified language and level."""
    try:
        language = request.language.lower()
        
        # Get recent suggestions for this language
        if language not in recent_suggestions:
            recent_suggestions[language] = []
        
        topic = get_topic_suggestion(
            request.level, 
            language=language,
            additional_excluded=recent_suggestions[language]
        )
        
        # Add to recent suggestions, keep list manageable
        if topic not in recent_suggestions[language]:
            recent_suggestions[language].append(topic)
            if len(recent_suggestions[language]) > 20:
                recent_suggestions[language].pop(0)
                
        return {"topic": topic, "language": language}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=LessonResponse)
def generate_lesson(request: LessonRequest):
    """Generate a complete lesson with story, vocabulary, grammar, quiz, and writing prompt."""
    try:
        language = request.language.lower()
        topic, markdown, html_content, lesson_data = generate_lesson_content(
            request.topic, 
            request.level,
            language=language
        )
        
        # Save to disk for history
        safe_topic = "".join([c for c in topic if c.isalnum() or c in (' ', '_')]).rstrip()
        base_filename = f"{language}_{safe_topic.replace(' ', '_').lower()}"
        
        output_dir = os.path.join(os.path.dirname(__file__), "output")
        os.makedirs(output_dir, exist_ok=True)

        md_path = os.path.join(output_dir, f"{base_filename}.md")
        html_path = os.path.join(output_dir, f"{base_filename}.html")
        json_path = os.path.join(output_dir, f"{base_filename}.json")
        
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(markdown)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html_content)
            
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(lesson_data, f, ensure_ascii=False, indent=2)
        
        return LessonResponse(
            topic=topic,
            level=request.level,
            language=language,
            lesson_plan=lesson_data.get("lesson_plan", ""),
            markdown_content=markdown,
            html_content=html_content,
            story=lesson_data.get("story", ""),
            vocabulary=lesson_data.get("vocabulary", []),
            grammar=lesson_data.get("grammar", []),
            quiz=lesson_data.get("quiz", []),
            writing_prompt=lesson_data.get("writing_prompt", None),
            filename=f"{base_filename}.html"
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============== Writing Endpoints ==============

@app.post("/writing/prompt")
def get_writing_prompt(request: WritingPromptRequest):
    """Generate a writing prompt for the specified topic and level."""
    try:
        return generate_writing_prompt(request.topic, request.level, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/writing/grade")
def grade_writing(request: WritingGradeRequest):
    """Grade a writing submission based on the given prompt."""
    try:
        return grade_writing_submission(request.submission, request.prompt, request.language)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ============== File History Endpoints (Legacy - for backward compatibility) ==============

@app.get("/file-history")
def get_file_history(language: Optional[str] = None):
    """List all generated lessons (HTML files) from local disk, optionally filtered by language."""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    if not os.path.exists(output_dir):
        return []
    
    files = []
    for f in os.listdir(output_dir):
        if f.endswith(".html"):
            # Get creation time
            path = os.path.join(output_dir, f)
            ctime = os.path.getctime(path)
            
            # Read metadata from JSON if available
            json_path = path.replace(".html", ".json")
            level = ""
            file_language = "chinese"  # Default for legacy files
            
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        level = data.get("level", "")
                        file_language = data.get("language", "chinese")
                except:
                    pass
            
            # Try to extract language from filename (new format: language_topic.html)
            if "_" in f:
                first_part = f.split("_")[0]
                if first_part in ["chinese", "english", "spanish"]:
                    file_language = first_part
                    topic_name = f.replace(f"{first_part}_", "").replace(".html", "").replace("_", " ").title()
                else:
                    topic_name = f.replace(".html", "").replace("_", " ").title()
            else:
                topic_name = f.replace(".html", "").replace("_", " ").title()
            
            # Filter by language if specified
            if language and file_language != language.lower():
                continue
            
            files.append({
                "filename": f,
                "topic": topic_name,
                "created_at": ctime,
                "level": level,
                "language": file_language
            })
    
    # Sort by newest first
    files.sort(key=lambda x: x["created_at"], reverse=True)
    return files

@app.get("/file-history/{filename}")
def get_lesson_file(filename: str):
    """Get the HTML content and JSON data of a specific lesson file."""
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    html_path = os.path.join(output_dir, filename)
    json_path = html_path.replace(".html", ".json")
    
    if not os.path.exists(html_path):
        raise HTTPException(status_code=404, detail="Lesson not found")
    
    result = {}
    
    with open(html_path, "r", encoding="utf-8") as f:
        result["html_content"] = f.read()
    
    # Try to load JSON data if available
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                result["lesson_data"] = json.load(f)
        except:
            result["lesson_data"] = None
    else:
        result["lesson_data"] = None

    return result


# ============== Health Check ==============

@app.get("/")
def root():
    return {
        "service": "Language Learning Agent Service",
        "version": "1.0.0",
        "endpoints": {
            "generate_lesson": "POST /generate",
            "suggest_topic": "POST /suggest-topic",
            "writing_prompt": "POST /writing/prompt",
            "grade_writing": "POST /writing/grade",
            "languages": "GET /languages"
        }
    }

@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "agent_service",
        "supported_languages": ["chinese", "english", "spanish"]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
