import os
import sys
import json
import re

# Add path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Crew, Process
from ChineseLearning.agents import ChineseLearningAgents
from ChineseLearning.tasks import ChineseLearningTasks
from dotenv import load_dotenv


load_dotenv()

def parse_json_from_text(text):
    """Attempt to extract and parse JSON from a text that might contain markdown or extra content."""
    # Try to find JSON array or object
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

def generate_interactive_html(lesson_data):
    """Generate a clean HTML page showing all agent outputs."""
    topic = lesson_data.get('topic', 'Lesson')
    level = lesson_data.get('level', 'HSK')
    lesson_plan = lesson_data.get('lesson_plan', '')
    story = lesson_data.get('story', '')
    vocabulary = lesson_data.get('vocabulary', [])
    grammar = lesson_data.get('grammar', [])
    
    # Convert markdown to HTML (basic)
    def md_to_html(text):
        lines = text.split('\n')
        result = []
        for line in lines:
            line = line.strip()
            if line.startswith('### '):
                result.append(f'<h4>{line[4:]}</h4>')
            elif line.startswith('## '):
                result.append(f'<h3>{line[3:]}</h3>')
            elif line.startswith('# '):
                result.append(f'<h2>{line[2:]}</h2>')
            elif line.startswith('- '):
                result.append(f'<li>{line[2:]}</li>')
            elif line.startswith('**') and line.endswith('**'):
                result.append(f'<strong>{line[2:-2]}</strong>')
            elif line:
                result.append(f'<p>{line}</p>')
        return '\n'.join(result)
    
    # Parse structured story using regex or split (simple split based on agent prompt)
    # Expected: # Story (Hanzi) ... # Pinyin ... # Translation ...
    story_parts = {'hanzi': '', 'pinyin': '', 'translation': ''}
    
    if '# Story' in story and '# Pinyin' in story and '# Translation' in story:
        try:
            # Simple manual parsing based on new structure
            parts = story.split('# Pinyin')
            hanzi_part = parts[0].replace('# Story (Hanzi)', '').replace('# Story', '').strip()
            
            remaining = parts[1]
            subparts = remaining.split('# Translation')
            pinyin_part = subparts[0].strip()
            trans_part = subparts[1].strip()
            
            story_parts['hanzi'] = hanzi_part
            story_parts['pinyin'] = pinyin_part
            story_parts['translation'] = trans_part
        except:
            # Fallback if structure is slightly off
            story_parts['hanzi'] = story
    else:
        # Fallback to legacy full text if keys missing
        story_parts['hanzi'] = story

    # Render Story HTML
    story_html = f'''
    <div class="story-block">
        <div class="story-hanzi">
            {md_to_html(story_parts['hanzi'])}
        </div>
    </div>
    '''
    
    if story_parts['pinyin']:
        story_html += f'''
        <details class="story-details">
            <summary>Show Pinyin</summary>
            <div class="story-pinyin">
                {md_to_html(story_parts['pinyin'])}
            </div>
        </details>
        '''
        
    if story_parts['translation']:
        story_html += f'''
        <details class="story-details">
            <summary>Show Translation</summary>
            <div class="story-trans">
                {md_to_html(story_parts['translation'])}
            </div>
        </details>
        '''
        
    # Validating lesson_plan_html to replace None with empty string
    lesson_plan_html = md_to_html(lesson_plan) if lesson_plan else ""
    
    # Build vocabulary HTML
    vocab_html = ""
    for item in vocabulary:
        hanzi = item.get('hanzi', '')
        pinyin = item.get('pinyin', '')
        meaning = item.get('meaning', '')
        
        # Example Sentence Logic
        example = item.get('example', '')
        example_pinyin = item.get('example_pinyin', '')
        example_meaning = item.get('example_meaning', '')
        
        example_block = ""
        if example:
            example_block = f'''
            <div style="margin-top:10px; padding-top:10px; border-top:1px dashed #e2e8f0;">
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-weight:500; font-size:0.95rem; color:#334155;">{example}</span>
                    <button onclick="speak('{example}')" style="background:none; border:none; cursor:pointer; font-size:0.85rem; opacity:0.6;">🔊</button>
                </div>
                <div style="font-size:0.85rem; color:#64748b; margin-top:2px;">{example_pinyin}</div>
                <div style="font-size:0.85rem; color:#94a3b8; font-style:italic; margin-top:1px;">{example_meaning}</div>
            </div>
            '''

        vocab_html += f'''
        <div class="vocab-row">
            <span class="hanzi">{hanzi}</span>
            <div class="vocab-info">
                <span class="pinyin">{pinyin}</span>
                <span class="meaning">{meaning}</span>
                {example_block}
            </div>
            <button class="tts-btn" onclick="speak('{hanzi}')">🔊</button>
        </div>
        '''
    
    # Build grammar HTML
    grammar_html = ""
    for item in grammar:
        pattern = item.get('pattern', '')
        explanation = item.get('explanation', '')
        example = item.get('example', '')
        grammar_html += f'''
        <div class="grammar-card">
            <div class="grammar-body">
                <div class="grammar-pattern">{pattern}</div>
                <div class="grammar-explanation">{explanation}</div>
                <div class="grammar-example-box">
                    <span class="grammar-example-badge">Example</span>
                    <div class="grammar-example-content">{example}</div>
                </div>
            </div>
        </div>
        '''

    html = f'''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {level}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Noto Sans SC', 'Inter', -apple-system, sans-serif;
            line-height: 1.8;
            color: #1f2937;
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 48px 32px;
            min-height: 100vh;
        }}
        .container {{ max-width: 760px; margin: 0 auto; }}
        
        .header {{
            text-align: center;
            margin-bottom: 48px;
            padding-bottom: 32px;
            border-bottom: 1px solid #e2e8f0;
        }}
        .badge {{
            display: inline-block;
            padding: 6px 16px;
            background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
            color: white;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 16px;
            box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
        }}
        h1 {{
            font-size: 2.25rem;
            font-weight: 800;
            color: #0f172a;
            margin-bottom: 8px;
            letter-spacing: -0.02em;
        }}
        .subtitle {{
            color: #64748b;
            font-size: 1rem;
        }}
        
        .section {{
            background: white;
            border-radius: 16px;
            padding: 28px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03);
            border: 1px solid #e2e8f0;
        }}
        
        .section-title {{
            font-size: 0.7rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            color: #3b82f6;
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        .section-title::before {{
            content: '';
            width: 3px;
            height: 16px;
            background: linear-gradient(180deg, #3b82f6 0%, #8b5cf6 100%);
            border-radius: 2px;
        }}
        
        h2, h3, h4 {{ color: #0f172a; margin: 20px 0 12px; }}
        h2 {{ font-size: 1.35rem; font-weight: 700; }}
        h3 {{ font-size: 1.15rem; font-weight: 600; }}
        h4 {{ font-size: 1rem; font-weight: 600; color: #475569; }}
        p {{ margin-bottom: 14px; color: #475569; line-height: 1.9; }}
        li {{ margin-left: 20px; margin-bottom: 8px; color: #475569; }}
        strong {{ color: #0f172a; }}
        
        .story-content {{
            font-size: 1.2rem;
            line-height: 2.2;
            color: #1e293b;
        }}
        .story-content p {{
            color: #1e293b;
            margin-bottom: 18px;
        }}
        
        .story-block {{
            background: #fff;
            border-radius: 8px;
            margin-bottom: 16px;
        }}
        .story-hanzi {{
            font-size: 1.3rem;
            line-height: 2;
            color: #0f172a;
            margin-bottom: 24px;
        }}
        
        details.story-details {{
            margin-top: 12px;
            margin-bottom: 12px;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            overflow: hidden;
            background: #f8fafc;
        }}
        details.story-details summary {{
            padding: 12px 16px;
            background: #f1f5f9;
            cursor: pointer;
            font-weight: 600;
            color: #475569;
            font-size: 0.9rem;
            list-style: none; /* Hide default triangle */
            display: flex;
            align-items: center;
            justify-content: space-between;
        }}
        details.story-details summary::after {{
            content: '+';
            font-weight: bold;
        }}
        details.story-details[open] summary::after {{
            content: '-';
        }}
        .story-pinyin, .story-trans {{
            padding: 16px;
            border-top: 1px solid #e2e8f0;
            color: #64748b;
            font-size: 1rem;
            line-height: 1.8;
        }}
        .story-pinyin {{ color: #8b5cf6; }} 

        
        .vocab-row {{
            display: grid;
            grid-template-columns: auto 1fr auto;
            gap: 20px;
            padding: 16px 20px;
            margin: 0 -20px;
            border-radius: 12px;
            align-items: center;
            transition: background 0.2s;
        }}
        .vocab-row:hover {{ background: #f8fafc; }}
        .hanzi {{ 
            font-size: 1.5rem; 
            font-weight: 700; 
            color: #0f172a;
            min-width: 80px;
        }}
        .vocab-info {{
            display: flex;
            flex-direction: column;
            gap: 4px;
        }}
        .pinyin {{ color: #8b5cf6; font-weight: 500; font-size: 0.95rem; }}
        .meaning {{ color: #64748b; font-size: 0.9rem; }}
        .tts-btn {{
            width: 36px;
            height: 36px;
            border: none;
            background: #f1f5f9;
            border-radius: 50%;
            cursor: pointer;
            font-size: 1rem;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .tts-btn:hover {{ background: #3b82f6; transform: scale(1.1); }}
        
        .grammar-card {{
            background: #ffffff;
            border-radius: 20px;
            margin-bottom: 28px;
            box-shadow: 0 20px 40px -12px rgba(0, 0, 0, 0.06);
            border: 1px solid rgba(255, 255, 255, 0.5);
            position: relative;
            overflow: hidden;
            transition: transform 0.2s;
        }}
        .grammar-card:hover {{
            transform: translateY(-2px);
        }}
        .grammar-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 6px;
            background: linear-gradient(90deg, #6366f1, #8b5cf6, #ec4899);
        }}
        .grammar-body {{
            padding: 28px 24px;
        }}
        .grammar-pattern {{
            font-size: 1.4rem;
            font-weight: 800;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            display: inline-block;
            font-family: 'Noto Sans SC', sans-serif;
            letter-spacing: -0.02em;
        }}
        .grammar-explanation {{
            color: #64748b;
            margin-bottom: 24px;
            line-height: 1.7;
            font-size: 1rem;
            font-weight: 400;
        }}
        .grammar-example-box {{
            background: #f8fafc;
            border-radius: 14px;
            padding: 18px 20px;
            border: 1px solid #f1f5f9;
            position: relative;
        }}
        .grammar-example-badge {{
            position: absolute;
            top: -10px;
            left: 16px;
            background: #fff;
            padding: 2px 10px;
            border-radius: 20px;
            font-size: 0.65rem;
            font-weight: 700;
            color: #6366f1;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            border: 1px solid #e2e8f0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.03);
        }}
        .grammar-example-content {{
            font-size: 1.05rem;
            color: #334155;
            font-weight: 500;
            line-height: 1.6;
        }}
        
        .footer {{
            text-align: center;
            padding: 32px 0 0;
            color: #94a3b8;
            font-size: 0.8rem;
        }}
    </style>
    <script>
        function speak(text) {{
            const u = new SpeechSynthesisUtterance(text);
            u.lang = 'zh-CN';
            u.rate = 0.85;
            speechSynthesis.speak(u);
        }}
    </script>
</head>
<body>
    <div class="container">
        <span class="badge">{level}</span>
        <h1>{topic}</h1>
        
        <div class="section">
            <div class="section-title">📋 Lesson Plan</div>
            {lesson_plan_html if lesson_plan_html else "<p>No lesson plan data.</p>"}
        </div>
        
        <div class="section">
            <div class="section-title">📖 Reading Passage</div>
            <div class="story-content">
                {story_html if story_html else "<p>No story data.</p>"}
            </div>
        </div>
        
        <div class="section">
            <div class="section-title">📝 Vocabulary ({len(vocabulary)} words)</div>
            {vocab_html if vocab_html else "<p>No vocabulary data.</p>"}
        </div>
        
        <div class="section">
            <div class="section-title">📐 Grammar Points</div>
            {grammar_html if grammar_html else "<p>No grammar data.</p>"}
        </div>
    </div>
</body>
</html>
'''
    return html

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-placeholder"

def generate_lesson_content(topic=None, level="HSK 5"):
    agents = ChineseLearningAgents()
    tasks = ChineseLearningTasks()

    planner = agents.lesson_planner_agent()
    writer = agents.content_writer_agent()
    linguist = agents.linguist_agent()
    examiner = agents.examiner_agent()
    
    crew_tasks = []
    
    # If no topic provided, generate one
    final_topic_name = topic
    if not topic:
        topic_task = tasks.suggest_topic_task(planner, level)
        crew_tasks.append(topic_task)
        print(f"Generating a random topic for {level}...")
        
    topic_description = topic if topic else "the topic suggested in the previous task"

    plan_task = tasks.plan_lesson_task(planner, topic_description, level)
    write_task = tasks.write_content_task(writer, topic_description, level)
    analyze_task = tasks.analyze_language_task(linguist)
    quiz_task = tasks.create_quiz_task(examiner)
    
    crew_tasks.extend([plan_task, write_task, analyze_task, quiz_task])

    # Sequential process: [Suggest] -> Plan -> Write -> Analyze -> Quiz
    crew = Crew(
        agents=[planner, writer, linguist, examiner],
        tasks=crew_tasks,
        verbose=True,
        process=Process.sequential
    )

    print(f"######################")
    print(f"Generating Lesson: {topic} ({level})")
    print(f"######################")
    
    result = crew.kickoff()
    
    # Parse outputs
    if not topic:
        generated_topic = str(crew_tasks[0].output).strip()
        generated_topic = generated_topic.replace("'", "").replace('"', "")
        final_topic_name = generated_topic
        task_offset = 1
    else:
        task_offset = 0
    
    # Get individual task outputs
    plan_output = str(crew_tasks[task_offset].output) if len(crew_tasks) > task_offset else ""
    story_output = str(crew_tasks[task_offset + 1].output) if len(crew_tasks) > task_offset + 1 else ""
    analyze_output = str(crew_tasks[task_offset + 2].output) if len(crew_tasks) > task_offset + 2 else ""
    quiz_output = str(crew_tasks[task_offset + 3].output) if len(crew_tasks) > task_offset + 3 else ""
    
    # Parse JSON from analyze and quiz outputs
    analyze_json = parse_json_from_text(analyze_output)
    quiz_json = parse_json_from_text(quiz_output)
    
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
            # New format with exercises array
            quiz = quiz_json.get('exercises', [])
        elif isinstance(quiz_json, list):
            # Legacy format - convert to new format with type
            quiz = []
            for q in quiz_json:
                if 'type' not in q:
                    q['type'] = 'multiple_choice'
                quiz.append(q)
    
    # Build lesson data
    lesson_data = {
        "topic": final_topic_name,
        "level": level,
        "lesson_plan": plan_output,
        "story": story_output,
        "vocabulary": vocabulary,
        "grammar": grammar,
        "quiz": quiz
    }
    
    # Generate markdown (legacy)
    body_output = ""
    headers = ["Lesson Plan", "Story", "Language Analysis", "Quiz"]
    for i, task in enumerate(crew_tasks[task_offset:]):
        header = headers[i] if i < len(headers) else f"Step {i+1}"
        body_output += f"## {header}\n\n"
        body_output += str(task.output) + "\n\n---\n\n"
    
    final_markdown = f"# Lesson: {final_topic_name} - {level}\n\n" + body_output
    
    # Generate interactive HTML
    html_content = generate_interactive_html(lesson_data)
    
    return final_topic_name, final_markdown, html_content, lesson_data

def get_topic_suggestion(level="HSK 3", additional_excluded=None):
    agents = ChineseLearningAgents()
    tasks = ChineseLearningTasks()
    
    # Get existing topics from disk to avoid repetition
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    disk_topics = []
    if os.path.exists(output_dir):
        disk_topics = [
            f.replace(".html", "").replace("_", " ").title() 
            for f in os.listdir(output_dir) 
            if f.endswith(".html")
        ]
    
    # Combine with extra topics (e.g. from current session)
    excluded_topics = list(set(disk_topics + (additional_excluded or [])))
    
    planner = agents.lesson_planner_agent()
    topic_task = tasks.suggest_topic_task(planner, level, excluded_topics)
    
    crew = Crew(
        agents=[planner],
        tasks=[topic_task],
        verbose=True,
        process=Process.sequential
    )
    
    result = crew.kickoff()
    topic = str(result).strip().replace("'", "").replace('"', "")
    return topic

def run(topic=None, level="HSK 5"):
    final_topic_name, full_output, html_content, lesson_data = generate_lesson_content(topic, level)
    
    # Generate Filename
    safe_topic = "".join([c for c in final_topic_name if c.isalnum() or c in (' ', '_')]).rstrip()
    base_filename = f"{safe_topic.replace(' ', '_').lower()}"
    
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
    if len(sys.argv) > 2:
        # python main.py "Topic" "HSK 5"
        run(topic=sys.argv[1], level=sys.argv[2])
    elif len(sys.argv) > 1:
        # python main.py "HSK 4" (Assume single arg is Level)
        run(level=sys.argv[1])
    else:
        # python main.py (Default HSK 5, Auto Topic)
        run()

