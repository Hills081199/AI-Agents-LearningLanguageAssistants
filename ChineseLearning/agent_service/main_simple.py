import os
import sys
import io
import json
import re
import time
from datetime import datetime

# Force UTF-8 encoding for stdout/stderr to handle Chinese characters on Windows
try:
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    if sys.stderr.encoding != 'utf-8':
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')
except Exception:
    pass

# Add current directory to path for imports when running directly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from crewai import Crew, Process
from agents import LanguageLearningAgents, ChineseLearningAgents, get_language_config, get_supported_languages
from tasks import LanguageLearningTasks, ChineseLearningTasks
from cache import cached_lesson, cache_manager
from dotenv import load_dotenv

load_dotenv()

def parse_json_from_text(text):
    """Attempt to extract and parse JSON from a text that might contain markdown or extra content."""
    text = str(text)
    # Remove markdown code blocks
    text = re.sub(r'```json\s*', '', text)
    text = re.sub(r'```\s*', '', text)
    
    # Try to find JSON object or array
    start_obj = text.find('{')
    start_arr = text.find('[')
    
    if start_obj == -1 and start_arr == -1:
        return None
    
    if start_arr != -1 and (start_obj == -1 or start_arr < start_obj):
        # Starts with array
        end = text.rfind(']')
        if end != -1:
            try:
                return json.loads(text[start_arr:end+1])
            except:
                pass
    else:
        # Starts with object
        end = text.rfind('}')
        if end != -1:
            try:
                return json.loads(text[start_obj:end+1])
            except:
                pass
    return None

def generate_interactive_html_fast(lesson_data, language="chinese"):
    """Generate HTML faster by using templates and reducing string operations."""
    config = get_language_config(language)
    tts_code = config.get("tts_code", "en-US")
    has_romanization = config.get("has_romanization", False)
    romanization_name = config.get("romanization_name", "Romanization")
    lang_name = config.get("name", "Language")
    
    topic = lesson_data.get('topic', 'Lesson')
    level = lesson_data.get('level', 'Level')
    story = lesson_data.get('story', '')
    vocabulary = lesson_data.get('vocabulary', [])
    grammar = lesson_data.get('grammar', [])
    
    # Simplified HTML template (faster generation)
    html_template = f'''<!DOCTYPE html>
<html lang="{tts_code[:2]}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {level}</title>
    <style>
        body {{ font-family: 'Inter', sans-serif; line-height: 1.6; color: #1f2937; background: #f8fafc; padding: 20px; }}
        .container {{ max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .badge {{ background: #3b82f6; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; margin: 0 4px; }}
        h1 {{ color: #1e293b; margin: 10px 0; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #e5e7eb; border-radius: 8px; }}
        .vocab-item {{ padding: 10px; border-bottom: 1px solid #f3f4f6; }}
        .vocab-item:last-child {{ border-bottom: none; }}
        .word {{ font-weight: bold; font-size: 1.2rem; color: #1e293b; }}
        .meaning {{ color: #6b7280; margin-top: 4px; }}
        .grammar-card {{ background: #f9fafb; padding: 15px; border-radius: 8px; margin: 10px 0; }}
        .pattern {{ font-weight: bold; color: #374151; }}
        .explanation {{ color: #6b7280; margin-top: 5px; }}
        .example {{ background: #e5e7eb; padding: 10px; border-radius: 4px; margin-top: 10px; font-style: italic; }}
    </style>
    <script>
        function speak(text) {{
            const u = new SpeechSynthesisUtterance(text);
            u.lang = '{tts_code}';
            u.rate = 0.85;
            speechSynthesis.speak(u);
        }}
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">{level}</span>
            <span class="badge">{lang_name}</span>
            <h1>{topic}</h1>
        </div>
        
        <div class="section">
            <h2>📖 Story</h2>
            <div>{story}</div>
        </div>
        
        <div class="section">
            <h2>📝 Vocabulary ({len(vocabulary)} words)</h2>
            {generate_vocab_html(vocabulary, has_romanization)}
        </div>
        
        <div class="section">
            <h2>📐 Grammar</h2>
            {generate_grammar_html(grammar)}
        </div>
    </div>
</body>
</html>'''
    
    return html_template

def generate_vocab_html(vocabulary, has_romanization):
    """Generate vocabulary HTML efficiently."""
    if not vocabulary:
        return "<p>No vocabulary available.</p>"
    
    vocab_items = []
    for item in vocabulary:
        word = item.get('word', item.get('hanzi', ''))
        romanization = item.get('romanization', item.get('pinyin', ''))
        meaning = item.get('meaning', '')
        
        vocab_html = f'''<div class="vocab-item">
            <div class="word">{word} <button onclick="speak('{word}')" style="background:none;border:none;cursor:pointer;">🔊</button></div>
            {"<div class='romanization'>{romanization}</div>" if romanization and has_romanization else ""}
            <div class="meaning">{meaning}</div>
        </div>'''
        vocab_items.append(vocab_html)
    
    return ''.join(vocab_items)

def generate_grammar_html(grammar):
    """Generate grammar HTML efficiently."""
    if not grammar:
        return "<p>No grammar points available.</p>"
    
    grammar_items = []
    for item in grammar:
        pattern = item.get('pattern', '')
        explanation = item.get('explanation', '')
        example = item.get('example', '')
        
        grammar_html = f'''<div class="grammar-card">
            <div class="pattern">{pattern}</div>
            <div class="explanation">{explanation}</div>
            {"<div class='example'>Example: {example}</div>" if example else ""}
        </div>'''
        grammar_items.append(grammar_html)
    
    return ''.join(grammar_items)

def generate_lesson_optimized(topic=None, level="HSK 5", language="chinese"):
    """Generate lesson using optimized sequential process (avoiding threading issues)."""
    agents = LanguageLearningAgents(language=language)
    tasks = LanguageLearningTasks(language=language)
    
    config = get_language_config(language)
    
    # Create agents
    planner = agents.lesson_planner_agent()
    writer = agents.content_writer_agent()
    linguist = agents.linguist_agent()
    examiner = agents.examiner_agent()
    writing_assessor = agents.writing_assessor_agent()
    
    start_time = time.time()
    
    # Step 1: Get topic (if not provided)
    final_topic = topic
    if not topic:
        topic_task = tasks.suggest_topic_task(planner, level)
        crew = Crew(agents=[planner], tasks=[topic_task], verbose=False, process=Process.sequential)
        result = crew.kickoff()
        final_topic = str(result).strip().replace("'", "").replace('"', "")
    
    # Step 2: Plan lesson (must be first)
    plan_task = tasks.plan_lesson_task(planner, final_topic, level)
    crew = Crew(agents=[planner], tasks=[plan_task], verbose=False, process=Process.sequential)
    plan_result = crew.kickoff()
    plan_output = str(plan_result)
    
    # Step 3: Execute content generation sequentially (avoid threading issues)
    write_task = tasks.write_content_task(writer, final_topic, level)
    crew = Crew(agents=[writer], tasks=[write_task], verbose=False, process=Process.sequential)
    write_result = crew.kickoff()
    story_output = str(write_result)
    
    # Step 4: Language analysis
    analyze_task = tasks.analyze_language_task(linguist)
    crew = Crew(agents=[linguist], tasks=[analyze_task], verbose=False, process=Process.sequential)
    analyze_result = crew.kickoff()
    analyze_output = str(analyze_result)
    
    # Step 5: Quiz creation
    quiz_task = tasks.create_quiz_task(examiner)
    crew = Crew(agents=[examiner], tasks=[quiz_task], verbose=False, process=Process.sequential)
    quiz_result = crew.kickoff()
    quiz_output = str(quiz_result)
    
    # Step 6: Writing prompt
    writing_prompt_task = tasks.generate_writing_prompt_task(writing_assessor, final_topic, level)
    crew = Crew(agents=[writing_assessor], tasks=[writing_prompt_task], verbose=False, process=Process.sequential)
    writing_prompt_result = crew.kickoff()
    writing_prompt_output = str(writing_prompt_result)
    
    # Parse JSON outputs
    analyze_json = parse_json_from_text(analyze_output)
    quiz_json = parse_json_from_text(quiz_output)
    writing_prompt_json = parse_json_from_text(writing_prompt_output)
    
    vocabulary = []
    grammar = []
    quiz = []
    
    if analyze_json:
        if isinstance(analyze_json, dict):
            vocabulary = analyze_json.get('vocabulary', [])
            grammar = analyze_json.get('grammar', [])
        elif isinstance(analyze_json, list):
            vocabulary = analyze_json
    
    if quiz_json:
        if isinstance(quiz_json, dict) and 'exercises' in quiz_json:
            quiz = quiz_json.get('exercises', [])
        elif isinstance(quiz_json, list):
            quiz = []
            for q in quiz_json:
                if 'type' not in q:
                    q['type'] = 'multiple_choice'
                quiz.append(q)
    
    # Build lesson data
    lesson_data = {
        "topic": final_topic,
        "level": level,
        "language": language,
        "lesson_plan": plan_output,
        "story": story_output,
        "vocabulary": vocabulary,
        "grammar": grammar,
        "quiz": quiz,
        "writing_prompt": writing_prompt_json
    }
    
    # Generate outputs
    body_output = f"# Lesson: {final_topic} - {level} ({language})\n\n"
    body_output += f"## Lesson Plan\n\n{plan_output}\n\n---\n\n"
    body_output += f"## Story\n\n{story_output}\n\n---\n\n"
    body_output += f"## Language Analysis\n\n{analyze_output}\n\n---\n\n"
    body_output += f"## Quiz\n\n{quiz_output}\n\n---\n\n"
    body_output += f"## Writing Prompt\n\n{writing_prompt_output}\n\n"
    
    final_markdown = body_output
    html_content = generate_interactive_html_fast(lesson_data, language)
    
    end_time = time.time()
    duration = end_time - start_time
    
    print(f"⚡ Lesson generated in {duration:.2f} seconds")
    
    return final_topic, final_markdown, html_content, lesson_data

# Apply caching decorator
@cached_lesson
def generate_lesson_content(topic=None, level="HSK 5", language="chinese"):
    """Cached version of lesson generation."""
    return generate_lesson_optimized(topic, level, language)

def get_topic_suggestion(level="HSK 3", language="chinese", additional_excluded=None):
    """Get topic suggestion with caching."""
    agents = LanguageLearningAgents(language=language)
    tasks = LanguageLearningTasks(language=language)
    
    # Check cache first
    cache_key = f"topic_{level}_{language}"
    cached_topic = cache_manager.get(cache_key, level, language)
    if cached_topic:
        return cached_topic.get('topic', 'Daily Life')
    
    planner = agents.lesson_planner_agent()
    topic_task = tasks.suggest_topic_task(planner, level, additional_excluded)
    
    crew = Crew(agents=[planner], tasks=[topic_task], verbose=False, process=Process.sequential)
    result = crew.kickoff()
    topic = str(result).strip().replace("'", "").replace('"', "")
    
    # Cache the topic
    cache_manager.set(cache_key, level, language, {'topic': topic})
    
    return topic

def generate_writing_prompt(topic, level, language="chinese"):
    """Generate writing prompt efficiently."""
    agents = LanguageLearningAgents(language=language)
    tasks = LanguageLearningTasks(language=language)
    
    assessor = agents.writing_assessor_agent()
    prompt_task = tasks.generate_writing_prompt_task(assessor, topic, level)
    
    crew = Crew(agents=[assessor], tasks=[prompt_task], verbose=False, process=Process.sequential)
    result = crew.kickoff()
    
    return parse_json_from_text(str(result))

def grade_writing_submission(submission, prompt_data, language="chinese"):
    """Grade writing submission efficiently."""
    agents = LanguageLearningAgents(language=language)
    tasks = LanguageLearningTasks(language=language)
    
    assessor = agents.writing_assessor_agent()
    grade_task = tasks.grade_writing_task(assessor, submission, prompt_data)
    
    crew = Crew(agents=[assessor], tasks=[grade_task], verbose=False, process=Process.sequential)
    result = crew.kickoff()
    
    return parse_json_from_text(str(result))

# Legacy function for backward compatibility
def run(topic=None, level="HSK 5", language="chinese"):
    """Run lesson generation with specified parameters."""
    final_topic_name, full_output, html_content, lesson_data = generate_lesson_content(topic, level, language)
    
    # Generate Filename
    safe_topic = "".join([c for c in final_topic_name if c.isalnum() or c in (' ', '_')]).rstrip()
    base_filename = f"{language}_{safe_topic.replace(' ', '_').lower()}"
    
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    md_path = os.path.join(output_dir, f"{base_filename}.md")
    html_path = os.path.join(output_dir, f"{base_filename}.html")
    json_path = os.path.join(output_dir, f"{base_filename}.json")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(full_output)
        
    print(f"\n\nLesson generated successfully: {md_path}")
    
    # Save HTML
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"HTML generated: {html_path}")
    
    # Save JSON
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(lesson_data, f, ensure_ascii=False, indent=2)
    print(f"JSON generated: {json_path}")

if __name__ == "__main__":
    if len(sys.argv) > 3:
        run(topic=sys.argv[1], level=sys.argv[2], language=sys.argv[3])
    elif len(sys.argv) > 2:
        run(topic=sys.argv[1], level=sys.argv[2])
    elif len(sys.argv) > 1:
        run(level=sys.argv[1])
    else:
        run()
