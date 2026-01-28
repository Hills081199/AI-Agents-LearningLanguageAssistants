from fastapi.responses import StreamingResponse
import asyncio
import json
from typing import AsyncGenerator

class StreamingLessonGenerator:
    """Streaming lesson generator for real-time feedback."""
    
    def __init__(self):
        self.status_messages = [
            "🔍 Analyzing request parameters...",
            "📝 Planning lesson structure...",
            "✍️ Generating story content...",
            "🔍 Analyzing vocabulary and grammar...",
            "📋 Creating quiz questions...",
            "✏️ Preparing writing prompt...",
            "🎨 Formatting lesson content...",
            "✅ Lesson generation complete!"
        ]
    
    async def generate_lesson_stream(self, topic: str, level: str, language: str) -> AsyncGenerator[str, None]:
        """Stream lesson generation progress."""
        try:
            # Send initial status
            yield self._format_message("status", "🚀 Starting lesson generation...")
            
            # Step 1: Topic generation (if needed)
            if not topic:
                yield self._format_message("status", "🎲 Generating topic...")
                await asyncio.sleep(0.5)  # Simulate processing
                # Here you would call the actual topic generation
                topic = f"Generated Topic for {level}"
                yield self._format_message("topic", {"topic": topic})
            
            # Step 2: Lesson planning
            yield self._format_message("status", "📋 Planning lesson structure...")
            await asyncio.sleep(1.0)
            # Here you would call actual lesson planning
            yield self._format_message("progress", {"step": 1, "total": 6, "message": "Lesson plan created"})
            
            # Step 3: Story generation
            yield self._format_message("status", "✍️ Generating story content...")
            await asyncio.sleep(2.0)
            # Here you would call actual story generation
            yield self._format_message("progress", {"step": 2, "total": 6, "message": "Story generated"})
            yield self._format_message("content_preview", {"story": "Story preview text..."})
            
            # Step 4: Language analysis
            yield self._format_message("status", "🔍 Analyzing vocabulary and grammar...")
            await asyncio.sleep(1.5)
            yield self._format_message("progress", {"step": 3, "total": 6, "message": "Language analysis complete"})
            yield self._format_message("content_preview", {"vocabulary_count": 10, "grammar_points": 3})
            
            # Step 5: Quiz creation
            yield self._format_message("status", "📋 Creating quiz questions...")
            await asyncio.sleep(1.0)
            yield self._format_message("progress", {"step": 4, "total": 6, "message": "Quiz created"})
            yield self._format_message("content_preview", {"quiz_count": 5})
            
            # Step 6: Writing prompt
            yield self._format_message("status", "✏️ Preparing writing prompt...")
            await asyncio.sleep(0.8)
            yield self._format_message("progress", {"step": 5, "total": 6, "message": "Writing prompt ready"})
            
            # Step 7: Final formatting
            yield self._format_message("status", "🎨 Formatting lesson content...")
            await asyncio.sleep(0.5)
            yield self._format_message("progress", {"step": 6, "total": 6, "message": "Content formatted"})
            
            # Generate final lesson (call actual optimized function)
            from main_optimized import generate_lesson_content
            final_topic, markdown, html, lesson_data = generate_lesson_content(topic, level, language)
            
            # Send final result
            yield self._format_message("complete", {
                "topic": final_topic,
                "markdown": markdown[:500] + "...",  # Preview
                "html": html[:500] + "...",  # Preview
                "lesson_data": lesson_data,
                "stats": {
                    "vocabulary_count": len(lesson_data.get("vocabulary", [])),
                    "grammar_count": len(lesson_data.get("grammar", [])),
                    "quiz_count": len(lesson_data.get("quiz", []))
                }
            })
            
        except Exception as e:
            yield self._format_message("error", {"message": str(e)})
    
    def _format_message(self, message_type: str, data: dict) -> str:
        """Format message for streaming."""
        return f"data: {json.dumps({'type': message_type, 'data': data})}\n\n"

# Global streaming generator
streaming_generator = StreamingLessonGenerator()

@app.post("/generate-stream")
async def generate_lesson_stream(request: LessonRequest):
    """Generate lesson with streaming progress updates."""
    language = request.language.lower()
    
    async def generate():
        async for message in streaming_generator.generate_lesson_stream(
            request.topic, request.level, language
        ):
            yield message
    
    return StreamingResponse(
        generate(),
        media_type="text/plain",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*"
        }
    )

@app.websocket("/ws/generate")
async def websocket_generate_lesson(websocket: WebSocket):
    """WebSocket endpoint for real-time lesson generation."""
    await websocket.accept()
    
    try:
        # Receive request parameters
        data = await websocket.receive_text()
        request_data = json.loads(data)
        
        topic = request_data.get("topic")
        level = request_data.get("level", "HSK 5")
        language = request_data.get("language", "chinese")
        
        # Stream generation progress
        async for message in streaming_generator.generate_lesson_stream(topic, level, language):
            await websocket.send_text(message)
            
    except WebSocketDisconnect:
        print("Client disconnected")
    except Exception as e:
        await websocket.send_text(f"data: {json.dumps({'type': 'error', 'data': {'message': str(e)}})}\n\n")
        await websocket.close()
