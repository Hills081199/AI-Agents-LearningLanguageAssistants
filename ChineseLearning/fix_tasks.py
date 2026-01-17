import os

file_path = 'tasks.py'
with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
    lines = f.readlines()

# Find the insertion point (before Backwards compatibility)
insert_idx = -1
for i, line in enumerate(lines):
    if "class ChineseLearningTasks" in line:
        insert_idx = i
        # Go back to find the comments/blank lines before it
        if i > 0 and lines[i-1].strip().startswith('#'):
             insert_idx = i-1
        if insert_idx > 0 and not lines[insert_idx-1].strip():
             insert_idx = insert_idx-1
        break

if insert_idx != -1:
    # Clean up garbage after the file (if any) by just taking up to the end of file from original read
    # But current file on disk has garbage appended at the VERY end.
    # The readlines() might have garbage at the end if I read the corrupted file.
    # I should ignore anything after Class ChineseLearningTasks block.
    # ChineseLearningTasks is small.
    
    # Let's reconstruct the file.
    # Keep lines up to insert_idx.
    # Add new code.
    # Add the remaining lines (ChineseLearningTasks class).
    
    # Read fresh content again but strict
    # Actually, lines will contain the original good content + garbage at end.
    # The garbage is likely after the ChineseLearningTasks class.
    
    # Let's just find where LanguageLearningTasks ends and insert there.
    # And keep the ChineseLearningTasks class.
    # And truncate anything after ChineseLearningTasks.
    
    # Easier: Just replace the file content with what I know + new code.
    # But I don't have the MIDDLE of the file in my prompt perfectly.
    
    # Strategy: Insert BEFORE "class ChineseLearningTasks"
    # And ensure "class ChineseLearningTasks" is preserved.
    # Drop anything after the ChineseLearningTasks class definition (lines 245-249 in original).
    # The garbage is line 250+.
    
    # Find start of ChineseLearningTasks
    cls_idx = -1
    for i, line in enumerate(lines):
        if "class ChineseLearningTasks" in line:
            cls_idx = i
            break
            
    if cls_idx != -1:
        # Keep everything up to comments before it
        split_idx = cls_idx
        if split_idx > 0 and lines[split_idx-1].strip().startswith('#'):
             split_idx -= 1
        if split_idx > 0 and not lines[split_idx-1].strip():
             split_idx -= 1
             
        # Content before insertion
        part1 = lines[:split_idx]
        
        # New code
        new_code = '''
    def generate_writing_prompt_task(self, agent, topic, level):
        return Task(
            description=(
                f"Create a stimulating writing prompt for specific topic: '{topic}' at level: '{level}' in {self.lang_name}. "
                "The prompt should encourage the student to practice vocabulary and grammar relevant to this level. "
                "You MUST output ONLY valid JSON. No markdown, no explanations.\\n\\n"
                "JSON Structure:\\n"
                "{\\n"
                '  "prompt_type": "essay",  // or letter, email, story, opinion\\n'
                '  "title": "Title of the prompt",\\n'
                '  "question": "The actual question or topic to write about",\\n'
                '  "context": "Background information or context for the writing",\\n'
                '  "requirements": ["Requirement 1", "Requirement 2"],\\n'
                '  "word_count_min": 150,\\n'
                '  "word_count_max": 250\\n'
                "}\\n\\n"
                "IMPORTANT: Start with { and end with }."
            ),
            expected_output='Valid JSON object containing the writing prompt details.',
            agent=agent
        )

    def grade_writing_task(self, agent, submission, prompt_data):
        return Task(
            description=(
                f"Evaluate the following {self.lang_name} writing submission based on the prompt.\\n\\n"
                f"PROMPT: {prompt_data}\\n\\n"
                f"SUBMISSION:\\n{submission}\\n\\n"
                "Grade the submission on a scale of 0-20 for each of the following 5 criteria:\\n"
                "1. Task Achievement / Relevance\\n"
                "2. Coherence & Cohesion\\n"
                "3. Organization / Structure\\n"
                "4. Idea Development\\n"
                "5. Language Accuracy (Grammar & Vocabulary)\\n\\n"
                "You MUST output ONLY valid JSON. No markdown, no explanations.\\n"
                "JSON Structure:\\n"
                "{\\n"
                '  "criteria_scores": {\\n'
                '    "task_achievement": 15,\\n'
                '    "coherence_cohesion": 16,\\n'
                '    "organization": 14,\\n'
                '    "idea_development": 15,\\n'
                '    "language_accuracy": 12\\n'
                '  },\\n'
                '  "total_score": 72,\\n'
                '  "overall_feedback": "General feedback paragraph...",\\n'
                '  "detailed_feedback": {\\n'
                '    "strengths": ["Strength 1", "Strength 2"],\\n'
                '    "weaknesses": ["Weakness 1", "Weakness 2"]\\n'
                '  },\\n'
                '  "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]\\n'
                "}\\n\\n"
                "IMPORTANT: Start with { and end with }."
            ),
            expected_output='Valid JSON object containing scores and detailed feedback.',
            agent=agent
        )

'''
        # The ChineseLearning class part
        # We need to ensure we don't include the garbage at the end
        # The class definition is short:
        # class ChineseLearningTasks(LanguageLearningTasks):
        #     """Backwards compatible alias for Chinese-only usage."""
        #     def __init__(self):
        #         super().__init__(language="chinese")
        # <EOF>
        
        part2 = lines[split_idx:cls_idx + 4] # take class def and init lines (approx 4-5 lines)
        
        # Write back
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(part1)
            f.write(new_code)
            f.writelines(part2)
            
print("Fixed tasks.py")
