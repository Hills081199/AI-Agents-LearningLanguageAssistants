from crewai import Task
import os
import sys
import random
from datetime import datetime

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agents import get_language_config, LANGUAGE_CONFIG


class LanguageLearningTasks:
    """Multi-language learning tasks supporting Chinese, English, and Spanish."""
    
    def __init__(self, language: str = "chinese"):
        self.language = language.lower()
        self.config = get_language_config(self.language)
        self.lang_name = self.config["name"]
        self.level_system = self.config["level_system"]
        self.has_romanization = self.config.get("has_romanization", False)
        self.romanization_name = self.config.get("romanization_name", "")
    
    def _get_content_length(self, level: str) -> str:
        """Get target content length based on language and level."""
        # Chinese HSK lengths
        if self.language == "chinese":
            hsk_lengths = {
                "HSK 1": "100-150 words",
                "HSK 2": "150-200 words",
                "HSK 3": "200-400 words",
                "HSK 4": "400-600 words",
                "HSK 5": "700-900 words",
                "HSK 6": "1000-1200 words"
            }
            for key, val in hsk_lengths.items():
                if key in level:
                    return val
            return "200-300 words"
        
        # CEFR lengths for English/Spanish
        cefr_lengths = {
            "A1": "80-120 words",
            "A2": "120-180 words",
            "B1": "200-350 words",
            "B2": "350-500 words",
            "C1": "500-700 words",
            "C2": "700-900 words"
        }
        for key, val in cefr_lengths.items():
            if key in level:
                return val
        return "200-300 words"
    
    def plan_lesson_task(self, agent, topic, level):
        return Task(
            description=(
                f"Create a detailed lesson plan for the topic: '{topic}' at level: '{level}' in {self.lang_name}. "
                "Outline the learning objectives, key vocabulary (5-10 words appropriate for this level), "
                "and two grammar points to cover. "
                "The output should be a structured outline."
            ),
            expected_output='A lesson plan outline with objectives, vocabulary list, and grammar points.',
            agent=agent
        )

    def suggest_topic_task(self, agent, level, excluded_topics=None):
        if excluded_topics is None:
            excluded_topics = []
            
        # Limit excluded topics
        recent_topics = ", ".join(excluded_topics[-30:]) if excluded_topics else "None"
        
        # Generate a random seed
        random_seed = random.randint(1, 100000)
        
        # Use language-specific topic categories
        categories = self.config.get("example_topics", [
            "Daily Life", "Travel", "Work", "Technology", "Culture"
        ])
        selected_category = random.choice(categories)
        
        # Add a diverse mood/style modifier
        styles = ["Creative", "Unconventional", "Deeply Cultural", "Practical", "Futuristic", "Traditional"]
        selected_style = random.choice(styles)
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")

        return Task(
            description=(
                f"Suggest a single, UNIQUE and UNCOMMON topic suitable for {self.level_system} level '{level}' in {self.lang_name}.\n"
                f"STYLE: {selected_style}\n"
                f"FOCUS DOMAIN: {selected_category} (You MUST choose a topic within this specific domain).\n\n"
                f"CRITICAL CONSTRAINT: You MUST NOT reuse any of these recent topics: [{recent_topics}].\n"
                f"CRITICAL CONSTRAINT: Avoid generic topics. Go for specific sub-topics or unique angles.\n"
                f"Random Context Token: {random_seed}-{timestamp}.\n\n"
                f"The topic should be interesting, specific, and culturally relevant to {self.lang_name}-speaking regions.\n"
                "Be highly creative! Look for unique angles or specific sub-topics rather than generic ones.\n"
                "Output ONLY the topic name."
            ),
            expected_output='A single string representing the topic.',
            agent=agent
        )

    def write_content_task(self, agent, topic, level):
        length = self._get_content_length(level)
        
        if self.has_romanization:
            # Chinese: Include Hanzi, Pinyin, and Translation
            output_instructions = (
                "You must output the content in THREE distinct sections:\n"
                f"1. **{self.lang_name} Text**: The text written in {self.lang_name}.\n"
                f"2. **{self.romanization_name}**: The full {self.romanization_name} transcription.\n"
                "3. **Translation**: The English translation.\n\n"
                f"Format as:\n"
                f"# Story ({self.lang_name})\n[Content]\n\n"
                f"# {self.romanization_name}\n[Content]\n\n"
                "# Translation\n[Content]"
            )
        else:
            # English/Spanish: Include target language text and translation
            if self.language == "english":
                output_instructions = (
                    "You must output the content in TWO distinct sections:\n"
                    "1. **English Text**: The story/passage written in English.\n"
                    "2. **Key Expressions**: Important phrases and idioms from the text with explanations.\n\n"
                    "Format as:\n"
                    "# Story (English)\n[Content]\n\n"
                    "# Key Expressions\n[List of important phrases with explanations]"
                )
            else:
                # Spanish
                output_instructions = (
                    "You must output the content in THREE distinct sections:\n"
                    "1. **Spanish Text**: The story/passage written in Spanish.\n"
                    "2. **Translation**: The English translation.\n"
                    "3. **Key Expressions**: Important phrases from the text.\n\n"
                    "Format as:\n"
                    "# Story (Español)\n[Content]\n\n"
                    "# Translation\n[Content]\n\n"
                    "# Key Expressions\n[List of important phrases]"
                )
                
        return Task(
            description=(
                f"Write a comprehensive reading passage (article or story) of approx {length} about '{topic}' following the provided lesson plan. "
                f"The content must be written in {self.lang_name}. "
                f"Ensure the language style and difficulty match the target {self.level_system} level defined in the plan.\n\n"
                "IMPORTANT: Write in continuous prose (paragraphs). Do NOT write a dialogue/script.\n"
                f"{output_instructions}"
            ),
            expected_output=f'A reading passage in {self.lang_name} formatted according to the specified structure.',
            agent=agent
        )

    def analyze_language_task(self, agent):
        if self.has_romanization:
            # Chinese: Include pinyin
            vocab_structure = (
                '{"word": "Word", "romanization": "pinyin/pronunciation", "meaning": "meaning", '
                '"example": "Example sentence.", "example_romanization": "Romanization for example.", '
                '"example_meaning": "English translation of example."}'
            )
            vocab_note = f"Include '{self.romanization_name}' romanization for all vocabulary."
        else:
            # English/Spanish: No romanization needed
            vocab_structure = (
                '{"word": "Word", "meaning": "definition/translation", "part_of_speech": "noun/verb/etc", '
                '"example": "Example sentence using the word.", "example_meaning": "Translation if not English."}'
            )
            vocab_note = "Include part of speech and clear definitions."
        
        return Task(
            description=(
                f"Analyze the story/passage created in the previous task ({self.lang_name}). "
                "You MUST output valid JSON. The structure MUST be:\n"
                "{\n"
                '  "vocabulary": [\n'
                f"    {vocab_structure},\n"
                "    ... (select 12-20 key words from the text) ...\n"
                "  ],\n"
                '  "grammar": [\n'
                '    {"pattern": "Pattern", "explanation": "Explanation...", "example": "Example..."},\n'
                "    ...more items...\n"
                "  ]\n"
                "}\n"
                f"{vocab_note}\n"
                "Extract 12-20 key vocabulary words (prioritize new or difficult words) and 3-5 grammar patterns."
            ),
            expected_output='Valid JSON object with vocabulary and grammar arrays.',
            agent=agent
        )

    def create_quiz_task(self, agent):
        if self.language == "chinese":
            fill_blank_example = '"sentence": "他去___买咖啡。", "answer": "商店", "hint": "A place to buy things (shāngdiàn)"'
            word_order_example = '"words": ["咖啡", "我", "喝", "想"], "answer": "我想喝咖啡"'
        elif self.language == "spanish":
            fill_blank_example = '"sentence": "Ella ___ al supermercado.", "answer": "va", "hint": "verb: to go (present tense)"'
            word_order_example = '"words": ["café", "yo", "quiero", "un"], "answer": "Yo quiero un café"'
        else:  # English
            fill_blank_example = '"sentence": "She ___ to the store yesterday.", "answer": "went", "hint": "past tense of go"'
            word_order_example = '"words": ["coffee", "I", "want", "some"], "answer": "I want some coffee"'
        
        return Task(
            description=(
                f"Create a diverse set of exercises based on the {self.lang_name} story and vocabulary. "
                "You MUST output ONLY valid JSON. No markdown code blocks, no explanations, just pure JSON.\n\n"
                "CREATE EXACTLY:\n"
                "- 10 multiple_choice questions (reading comprehension)\n"
                "- 5 fill_blank exercises (vocabulary in context)\n"
                "- 1 matching exercise with 5 word pairs\n"
                "- 5 sentence_order exercises (grammar practice)\n\n"
                "The JSON must follow this exact structure:\n"
                "{\n"
                '  "exercises": [\n'
                "    {\n"
                '      "type": "multiple_choice",\n'
                '      "question": "What did the character do?",\n'
                '      "options": ["A. Option1", "B. Option2", "C. Option3", "D. Option4"],\n'
                '      "answer": "A",\n'
                '      "explanation": "Explanation of the correct answer."\n'
                "    },\n"
                "    {\n"
                '      "type": "fill_blank",\n'
                f"      {fill_blank_example},\n"
                '      "explanation": "Explanation."\n'
                "    },\n"
                "    {\n"
                '      "type": "matching",\n'
                '      "pairs": [\n'
                '        {"word": "word1", "meaning": "meaning1"},\n'
                '        {"word": "word2", "meaning": "meaning2"}\n'
                "      ]\n"
                "    },\n"
                "    {\n"
                '      "type": "sentence_order",\n'
                f"      {word_order_example},\n"
                '      "translation": "English translation."\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "IMPORTANT: Start your response with { and end with }. Do NOT wrap in markdown code blocks."
            ),
            expected_output='Valid JSON object with exercises array containing diverse quiz types.',
            agent=agent
        )

    def generate_writing_prompt_task(self, agent, topic, level):
        return Task(
            description=(
                f"Create a stimulating writing prompt for specific topic: '{topic}' at level: '{level}' in {self.lang_name}. "
                "The prompt should encourage the student to practice vocabulary and grammar relevant to this level. "
                "You MUST output ONLY valid JSON. No markdown, no explanations.\n\n"
                "JSON Structure:\n"
                "{\n"
                '  "prompt_type": "essay",  // or letter, email, story, opinion\n'
                '  "title": "Title of the prompt",\n'
                '  "question": "The actual question or topic to write about",\n'
                '  "context": "Background information or context for the writing",\n'
                '  "requirements": ["Requirement 1", "Requirement 2"],\n'
                '  "word_count_min": 150,\n'
                '  "word_count_max": 250\n'
                "}\n\n"
                "IMPORTANT: Start with { and end with }."
            ),
            expected_output='Valid JSON object containing the writing prompt details.',
            agent=agent
        )

    def grade_writing_task(self, agent, submission, prompt_data):
        return Task(
            description=(
                f"Evaluate the following {self.lang_name} writing submission based on the prompt.\n\n"
                f"PROMPT: {prompt_data}\n\n"
                f"SUBMISSION:\n{submission}\n\n"
                "Grade the submission on a scale of 0-20 for each of the following 5 criteria:\n"
                "1. Task Achievement / Relevance\n"
                "2. Coherence & Cohesion\n"
                "3. Organization / Structure\n"
                "4. Idea Development\n"
                "5. Language Accuracy (Grammar & Vocabulary)\n\n"
                "You MUST output ONLY valid JSON. No markdown, no explanations.\n"
                "JSON Structure:\n"
                "{\n"
                '  "criteria_scores": {\n'
                '    "task_achievement": 15,\n'
                '    "coherence_cohesion": 16,\n'
                '    "organization": 14,\n'
                '    "idea_development": 15,\n'
                '    "language_accuracy": 12\n'
                '  },\n'
                '  "total_score": 72,\n'
                '  "overall_feedback": "General feedback paragraph...",\n'
                '  "detailed_feedback": {\n'
                '    "strengths": ["Strength 1", "Strength 2"],\n'
                '    "weaknesses": ["Weakness 1", "Weakness 2"]\n'
                '  },\n'
                '  "improvement_suggestions": ["Suggestion 1", "Suggestion 2"]\n'
                "}\n\n"
                "IMPORTANT: Start with { and end with }."
            ),
            expected_output='Valid JSON object containing scores and detailed feedback.',
            agent=agent
        )


# Backwards compatibility - keep the old class name as alias
class ChineseLearningTasks(LanguageLearningTasks):
    """Backwards compatible alias for Chinese-only usage."""
    def __init__(self):
        super().__init__(language="chinese")
