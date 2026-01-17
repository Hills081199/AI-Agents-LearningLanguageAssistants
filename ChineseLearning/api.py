
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Any
import os
import sys
import json

# Add path to allow imports from local directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ChineseLearning.main import generate_lesson_content, get_topic_suggestion

app = FastAPI(title="HSK Content Factory API")

# Allow requests from any origin (flexible for EC2/Production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global cache for recently suggested topics to avoid repetitive "Random Topic" results
recent_suggestions = []

class LessonRequest(BaseModel):
    topic: Optional[str] = None
    level: str = "HSK 5"

class LessonResponse(BaseModel):
    topic: str
    level: str
    markdown_content: str
    html_content: str
    story: str
    vocabulary: List[Any] = []
    grammar: List[Any] = []
    quiz: List[Any] = []

class TopicRequest(BaseModel):
    level: str = "HSK 3"

@app.post("/suggest-topic")
def suggest_topic(request: TopicRequest):
    try:
        topic = get_topic_suggestion(request.level, additional_excluded=recent_suggestions)
        
        # Add to recent suggestions, keep list manageable
        if topic not in recent_suggestions:
            recent_suggestions.append(topic)
            if len(recent_suggestions) > 20:
                recent_suggestions.pop(0)
                
        return {"topic": topic}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=LessonResponse)
def generate_lesson(request: LessonRequest):
    try:
        topic, markdown, html_content, lesson_data = generate_lesson_content(request.topic, request.level)
        
        # Save to disk for history
        safe_topic = "".join([c for c in topic if c.isalnum() or c in (' ', '_')]).rstrip()
        base_filename = f"{safe_topic.replace(' ', '_').lower()}"
        
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
            markdown_content=markdown,
            html_content=html_content,
            story=lesson_data.get("story", ""),
            vocabulary=lesson_data.get("vocabulary", []),
            grammar=lesson_data.get("grammar", []),
            quiz=lesson_data.get("quiz", [])
        )
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/history")
def get_history():
    """List all generated lessons (html files)"""
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
            if os.path.exists(json_path):
                try:
                    with open(json_path, "r", encoding="utf-8") as jf:
                        data = json.load(jf)
                        level = data.get("level", "")
                except:
                    pass
            
            files.append({
                "filename": f,
                "topic": f.replace(".html", "").replace("_", " ").title(),
                "created_at": ctime,
                "level": level
            })
    
    # Sort by new to old
    files.sort(key=lambda x: x["created_at"], reverse=True)
    return files

@app.get("/history/{filename}")
def get_lesson_html(filename: str):
    """Get the HTML content and JSON data of a specific lesson"""
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

@app.get("/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

