import os
import sys
import json
import re

# Add path to allow imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from crewai import Crew, Process
from ChineseLearning.agents import LanguageLearningAgents, ChineseLearningAgents, get_language_config, get_supported_languages
from ChineseLearning.tasks import LanguageLearningTasks, ChineseLearningTasks
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

def generate_interactive_html(lesson_data, language="chinese"):
    """Generate a clean HTML page showing all agent outputs."""
    config = get_language_config(language)
    tts_code = config.get("tts_code", "en-US")
    has_romanization = config.get("has_romanization", False)
    romanization_name = config.get("romanization_name", "Romanization")
    lang_name = config.get("name", "Language")
    
    topic = lesson_data.get('topic', 'Lesson')
    level = lesson_data.get('level', 'Level')
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
    
    # Parse structured story - handles multiple format styles
    story_parts = {'main': '', 'romanization': '', 'translation': '', 'expressions': ''}
    
    # Try to parse based on language
    if language == "chinese":
        if '# Story' in story and '# Pinyin' in story and '# Translation' in story:
            try:
                parts = story.split('# Pinyin')
                hanzi_part = parts[0].replace('# Story (Chinese)', '').replace('# Story (中文)', '').replace('# Story', '').strip()
                remaining = parts[1]
                subparts = remaining.split('# Translation')
                pinyin_part = subparts[0].strip()
                trans_part = subparts[1].strip()
                
                story_parts['main'] = hanzi_part
                story_parts['romanization'] = pinyin_part
                story_parts['translation'] = trans_part
            except:
                story_parts['main'] = story
        else:
            story_parts['main'] = story
    elif language == "spanish":
        if '# Story' in story and '# Translation' in story:
            try:
                parts = story.split('# Translation')
                main_part = parts[0].replace('# Story (Español)', '').replace('# Story (Spanish)', '').replace('# Story', '').strip()
                remaining = parts[1] if len(parts) > 1 else ""
                
                if '# Key Expressions' in remaining:
                    subparts = remaining.split('# Key Expressions')
                    trans_part = subparts[0].strip()
                    expr_part = subparts[1].strip() if len(subparts) > 1 else ""
                else:
                    trans_part = remaining.strip()
                    expr_part = ""
                
                story_parts['main'] = main_part
                story_parts['translation'] = trans_part
                story_parts['expressions'] = expr_part
            except:
                story_parts['main'] = story
        else:
            story_parts['main'] = story
    else:  # English
        if '# Story' in story:
            try:
                if '# Key Expressions' in story:
                    parts = story.split('# Key Expressions')
                    main_part = parts[0].replace('# Story (English)', '').replace('# Story', '').strip()
                    expr_part = parts[1].strip()
                    story_parts['main'] = main_part
                    story_parts['expressions'] = expr_part
                else:
                    story_parts['main'] = story.replace('# Story (English)', '').replace('# Story', '').strip()
            except:
                story_parts['main'] = story
        else:
            story_parts['main'] = story

    # Render Story HTML
    story_html = f'''
    <div class="story-block">
        <div class="story-main">
            {md_to_html(story_parts['main'])}
        </div>
    </div>
    '''
    
    if story_parts['romanization']:
        story_html += f'''
        <details class="story-details">
            <summary>Show {romanization_name}</summary>
            <div class="story-romanization">
                {md_to_html(story_parts['romanization'])}
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
    
    if story_parts['expressions']:
        story_html += f'''
        <details class="story-details">
            <summary>Show Key Expressions</summary>
            <div class="story-expressions">
                {md_to_html(story_parts['expressions'])}
            </div>
        </details>
        '''
        
    # Validating lesson_plan_html to replace None with empty string
    lesson_plan_html = md_to_html(lesson_plan) if lesson_plan else ""
    
    # Build vocabulary HTML - adapt for different languages
    vocab_html = ""
    for item in vocabulary:
        # Handle different vocabulary field names
        word = item.get('word', item.get('hanzi', ''))
        romanization = item.get('romanization', item.get('pinyin', ''))
        meaning = item.get('meaning', '')
        part_of_speech = item.get('part_of_speech', '')
        
        # Example Sentence Logic
        example = item.get('example', '')
        example_romanization = item.get('example_romanization', item.get('example_pinyin', ''))
        example_meaning = item.get('example_meaning', '')
        
        example_block = ""
        if example:
            example_block = f'''
            <div style="margin-top:10px; padding-top:10px; border-top:1px dashed #e2e8f0;">
                <div style="display:flex; align-items:center; gap:6px;">
                    <span style="font-weight:500; font-size:0.95rem; color:#334155;">{example}</span>
                    <button onclick="speak('{example}')" style="background:none; border:none; cursor:pointer; font-size:0.85rem; opacity:0.6;">🔊</button>
                </div>
                {"<div style='font-size:0.85rem; color:#64748b; margin-top:2px;'>" + example_romanization + "</div>" if example_romanization else ""}
                {"<div style='font-size:0.85rem; color:#94a3b8; font-style:italic; margin-top:1px;'>" + example_meaning + "</div>" if example_meaning else ""}
            </div>
            '''
        
        # Build vocab info section
        vocab_info_parts = []
        if romanization and has_romanization:
            vocab_info_parts.append(f'<span class="romanization">{romanization}</span>')
        if part_of_speech:
            vocab_info_parts.append(f'<span class="pos">{part_of_speech}</span>')
        vocab_info_parts.append(f'<span class="meaning">{meaning}</span>')
        
        vocab_html += f'''
        <div class="vocab-row">
            <span class="word">{word}</span>
            <div class="vocab-info">
                {" ".join(vocab_info_parts)}
                {example_block}
            </div>
            <button class="tts-btn" onclick="speak('{word}')">🔊</button>
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
<html lang="{tts_code[:2]}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{topic} - {level}</title>
    <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700&family=Inter:wght@400;5606&display=swap" rel="stylesheet">
    <style>
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            font-family: 'Inter', 'Noto Sans SC', -apple-system, sans-serif;
            line-height: 1.8;
            color: #1f2937;
            background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
            padding: 48px 32px;
            min-height: 100vh;
        }}
        .container {{ max-width: 880px; margin: 0 auto; }}
        
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
            margin-right: 8px;
        }}
        .lang-badge {{
            display: inline-block;
            padding: 6px 16px;
            background: linear-gradient(135deg, #10b981 0%, #14b8a6 100%);
            color: white;
            border-radius: 9999px;
            font-size: 0.75rem;
            font-weight: 600;
            margin-bottom: 16px;
        }}
        h1 {{
            font-size: 2.5rem;
            font-weight: 900;
            background: linear-gradient(135deg, #1e293b 0%, #475569 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -0.03em;
            margin-bottom: 12px;
        }}
        
        /* Tab Navigation */
        .tab-nav {{
            display: flex;
            gap: 8px;
            margin-bottom: 28px;
            border-bottom: 2px solid #e2e8f0;
            flex-wrap: wrap;
        }}
        .tab-btn {{
            padding: 12px 24px;
            background: none;
            border: none;
            cursor: pointer;
            font-size: 0.95rem;
            font-weight: 600;
            color: #64748b;
            position: relative;
            transition: all 0.2s;
            border-radius: 8px 8px 0 0;
        }}
        .tab-btn:hover {{
            color: #3b82f6;
            background: #f1f5f9;
        }}
        .tab-btn.active {{
            color: #3b82f6;
            background: white;
        }}
        .tab-btn.active::after {{
            content: '';
            position: absolute;
            bottom: -2px;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #3b82f6, #8b5cf6);
            border-radius: 999px;
        }}
        
        .tab-content {{
            display: none;
        }}
        .tab-content.active {{
            display: block;
            animation: fadeIn 0.3s ease-in;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        /* Section styles */
        .section {{
            background: white;
            border-radius: 16px;
            padding: 32px;
            margin-bottom: 24px;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }}
        .section-title {{
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 24px;
            color: #0f172a;
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        /* Lesson Plan specific */
        .lesson-plan-content {{
            line-height: 2;
        }}
        .lesson-plan-content h2 {{
            color: #1e293b;
            margin: 24px 0 12px 0;
            font-size: 1.4rem;
        }}
        .lesson-plan-content h3 {{
            color: #334155;
            margin: 18px 0 10px 0;
            font-size: 1.2rem;
        }}
        .lesson-plan-content h4 {{
            color: #475569;
            margin: 14px 0 8px 0;
            font-size: 1.05rem;
        }}
        .lesson-plan-content p {{
            margin: 8px 0;
            color: #64748b;
        }}
        .lesson-plan-content li {{
            margin-left: 24px;
            color: #64748b;
            margin-bottom: 6px;
        }}
        .lesson-plan-content strong {{
            color: #1e293b;
            font-weight: 600;
        }}
        
        /* Story styles */
        .story-section {{
            margin-bottom: 32px;
            padding: 24px;
            border-radius: 14px;
        }}
        .story-section.main {{
            background: linear-gradient(to bottom right, #f8fafc, #ffffff);
            border: 1px solid #e2e8f0;
        }}
        .story-section.romanization {{
            background: linear-gradient(to bottom right, #fef3c7, #fef9e7);
            border: 1px solid #fde047;
        }}
        .story-section.translation {{
            background: linear-gradient(to bottom right, #dbeafe, #eff6ff);
            border: 1px solid #93c5fd;
        }}
        .story-section.expressions {{
            background: linear-gradient(to bottom right, #e0e7ff, #f5f3ff);
            border: 1px solid #c7d2fe;
        }}
        .story-section-title {{
            font-size: 0.85rem;
            text-transform: uppercase;
            font-weight: 700;
            letter-spacing: 0.05em;
            margin-bottom: 14px;
            opacity: 0.7;
        }}
        .story-text {{
            line-height: 2.2;
            font-size: 1.05rem;
        }}
        .story-section.main .story-text {{
            font-size: 1.25rem;
            font-weight: 500;
            color: #0f172a;
        }}
        .story-section.romanization .story-text {{
            color: #92400e;
            font-style: italic;
        }}
        .story-section.translation .story-text {{
            color: #1e40af;
        }}
        .story-section.expressions .story-text {{
            color: #4c1d95;
        }}
        
        /* Vocabulary styles */
        .vocab-row {{
            display: flex;
            align-items: flex-start;
            padding: 18px;
            border-bottom: 1px solid #f1f5f9;
            gap: 18px;
            transition: background 0.15s;
        }}
        .vocab-row:hover {{
            background: #f8fafc;
        }}
        .vocab-row:last-child {{
            border-bottom: none;
        }}
        .word {{
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            min-width: 140px;
        }}
        .vocab-info {{
            flex: 1;
        }}
        .romanization {{
            color: #8b5cf6;
            font-size: 0.9rem;
            font-weight: 500;
            margin-right: 10px;
        }}
        .pos {{
            color: #64748b;
            font-size: 0.8rem;
            font-style: italic;
            padding: 2px 8px;
            background: #f1f5f9;
            border-radius: 4px;
            margin-right: 10px;
        }}
        .meaning {{
            color: #475569;
            font-size: 1rem;
        }}
        .tts-btn {{
            background: none;
            border: 1px solid #e2e8f0;
            border-radius: 8px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 1.2rem;
            transition: all 0.2s;
        }}
        .tts-btn:hover {{
            background: #f8fafc;
            border-color: #cbd5e1;
            transform: scale(1.1);
        }}
        
        /* Grammar styles */
        .grammar-card {{
            background: white;
            border-radius: 16px;
            margin-bottom: 24px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
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
            border-left: 4px solid #8b5cf6;
        }}
        .grammar-example-badge {{
            display: inline-block;
            background: #8b5cf6;
            color: white;
            font-size: 0.7rem;
            padding: 3px 10px;
            border-radius: 999px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.03em;
            margin-bottom: 10px;
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
            u.lang = '{tts_code}';
            u.rate = 0.85;
            speechSynthesis.speak(u);
        }}
        
        function switchTab(tabName) {{
            // Hide all tabs
            const tabs = document.querySelectorAll('.tab-content');
            tabs.forEach(tab => tab.classList.remove('active'));
            
            const buttons = document.querySelectorAll('.tab-btn');
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Show selected tab
            document.getElementById(tabName).classList.add('active');
        }}
        
        // Expose function globally
        window.switchTab = switchTab;
        

    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <span class="badge">{level}</span>
            <span class="lang-badge">{lang_name}</span>
            <h1>{topic}</h1>
        </div>
        
        <div class="tab-nav" style="display: none;">
             <!-- Hidden tab nav, controlled by parent -->
        </div>
        
        <!-- Lesson Plan Tab -->
        <div id="lesson-plan" class="tab-content active">
            <div class="section">
                <div class="section-title">🎯 Lesson Objectives</div>
                <div class="lesson-plan-content">
                    {lesson_plan_html}
                </div>
            </div>
        </div>
        
        <!-- Story Tab (Combined Reading, Vocab, Grammar) -->
        <div id="story" class="tab-content">
            <div class="section">
                <div class="section-title">📖 Reading Passage</div>
                {story_html if story_html else "<p>No story data.</p>"}
            </div>
            
            <div class="section" style="margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 40px;">
                <div class="section-title">📝 Vocabulary ({len(vocabulary)} words)</div>
                {vocab_html if vocab_html else "<p>No vocabulary data.</p>"}
            </div>
            
            <div class="section" style="margin-top: 40px; border-top: 1px solid #e2e8f0; padding-top: 40px;">
                <div class="section-title">📐 Grammar Points</div>
                {grammar_html if grammar_html else "<p>No grammar data.</p>"}
            </div>
        </div>
    </div>
</body>
</html>
'''
    return html

if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-placeholder"

def generate_lesson_content(topic=None, level="HSK 5", language="chinese"):
    """Generate lesson content for the specified language and level."""
    # Use new multi-language classes
    agents = LanguageLearningAgents(language=language)
    tasks = LanguageLearningTasks(language=language)
    
    config = get_language_config(language)
    level_system = config.get("level_system", "Level")

    planner = agents.lesson_planner_agent()
    writer = agents.content_writer_agent()
    linguist = agents.linguist_agent()
    examiner = agents.examiner_agent()
    writing_assessor = agents.writing_assessor_agent()

    
    crew_tasks = []
    
    # If no topic provided, generate one
    final_topic_name = topic
    if not topic:
        topic_task = tasks.suggest_topic_task(planner, level)
        crew_tasks.append(topic_task)
        print(f"Generating a random topic for {level} ({language})...")
        
    topic_description = topic if topic else "the topic suggested in the previous task"

    plan_task = tasks.plan_lesson_task(planner, topic_description, level)
    write_task = tasks.write_content_task(writer, topic_description, level)
    analyze_task = tasks.analyze_language_task(linguist)
    quiz_task = tasks.create_quiz_task(examiner)
    writing_prompt_task = tasks.generate_writing_prompt_task(writing_assessor, topic_description, level)
    
    crew_tasks.extend([plan_task, write_task, analyze_task, quiz_task, writing_prompt_task])

    # Sequential process: [Suggest] -> Plan -> Write -> Analyze -> Quiz -> Writing Prompt
    crew = Crew(
        agents=[planner, writer, linguist, examiner, writing_assessor],
        tasks=crew_tasks,
        verbose=True,
        process=Process.sequential
    )

    print(f"######################")
    print(f"Generating Lesson: {topic} ({level}) - {language.upper()}")
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
    analyze_output = str(crew_tasks[task_offset + 2].output) if len(crew_tasks) > task_offset + 2 else ""
    quiz_output = str(crew_tasks[task_offset + 3].output) if len(crew_tasks) > task_offset + 3 else ""
    writing_prompt_output = str(crew_tasks[task_offset + 4].output) if len(crew_tasks) > task_offset + 4 else ""
    
    # Parse JSON from outputs
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
        "language": language,
        "lesson_plan": plan_output,
        "story": story_output,
        "vocabulary": vocabulary,
        "grammar": grammar,
        "quiz": quiz,
        "writing_prompt": writing_prompt_json
    }
    
    # Generate markdown (legacy)
    body_output = ""
    headers = ["Lesson Plan", "Story", "Language Analysis", "Quiz", "Writing Prompt"]
    for i, task in enumerate(crew_tasks[task_offset:]):
        header = headers[i] if i < len(headers) else f"Step {i+1}"
        body_output += f"## {header}\n\n"
        body_output += str(task.output) + "\n\n---\n\n"
    
    final_markdown = f"# Lesson: {final_topic_name} - {level} ({language})\n\n" + body_output
    
    # Generate interactive HTML
    html_content = generate_interactive_html(lesson_data, language)
    
    return final_topic_name, final_markdown, html_content, lesson_data

def get_topic_suggestion(level="HSK 3", language="chinese", additional_excluded=None):
    """Get a random topic suggestion for the specified language and level."""
    agents = LanguageLearningAgents(language=language)
    tasks = LanguageLearningTasks(language=language)
    
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
        # python main.py "Topic" "HSK 5" "chinese"
        run(topic=sys.argv[1], level=sys.argv[2], language=sys.argv[3])
    elif len(sys.argv) > 2:
        # python main.py "Topic" "HSK 5" (default Chinese)
        run(topic=sys.argv[1], level=sys.argv[2])
    elif len(sys.argv) > 1:
        # python main.py "HSK 4" (Assume single arg is Level, default Chinese)
        run(level=sys.argv[1])
    else:
        # python main.py (Default HSK 5, Auto Topic, Chinese)
        run()


def generate_writing_prompt(topic, level, language="chinese"):

    """Generate a writing prompt using the writing agent."""

    agents = LanguageLearningAgents(language=language)

    tasks = LanguageLearningTasks(language=language)

    

    assessor = agents.writing_assessor_agent()

    prompt_task = tasks.generate_writing_prompt_task(assessor, topic, level)

    

    crew = Crew(

        agents=[assessor],

        tasks=[prompt_task],

        verbose=True

    )

    

    result = crew.kickoff()

    return parse_json_from_text(str(result))



def grade_writing_submission(submission, prompt_data, language="chinese"):

    """Grade a writing submission using the writing agent."""

    agents = LanguageLearningAgents(language=language)

    tasks = LanguageLearningTasks(language=language)

    

    assessor = agents.writing_assessor_agent()

    grade_task = tasks.grade_writing_task(assessor, submission, prompt_data)

    

    crew = Crew(

        agents=[assessor],

        tasks=[grade_task],

        verbose=True

    )

    

    result = crew.kickoff()

    return parse_json_from_text(str(result))

