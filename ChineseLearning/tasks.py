from crewai import Task
import random
from datetime import datetime

class ChineseLearningTasks:
    def plan_lesson_task(self, agent, topic, level):
        return Task(
            description=(
                f"Create a detailed lesson plan for the topic: '{topic}' at level: '{level}'. "
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
        
        # Select a random thematic category to force diversity
        categories = [
            "Ancient History & Legends", "Modern Technology & Innovation", 
            "Traditional Festivals & Customs", "Cuisine & Food Culture",
            "Travel & Geography of China", "Modern Business & Economy", 
            "Arts, Music & Entertainment", "Daily Life & Relationships",
            "Health, Wellness & TCM", "Environment & Nature",
            "Education & Campus Life", "Social Trends & Hot Topics",
            "Famous Biographies", "Science & Discovery", "Literature & Idioms",
            "Philosophy & Wisdom", "Internet Culture & Slang",
            "Urban Trends & City Life", "Rural Countryside & Agriculture",
            "Architecture & Housing", "Martial Arts & Kung Fu",
            "Calligraphy & Painting", "Chinese Zodiac & Astrology",
            "Family Dynamics & Parenting", "Wedding Customs & Marriage",
            "Etiquette & Social Politeness", "Public Transport & Commuting",
            "Online Shopping & E-commerce", "Esports & Gaming",
            "Workplace Culture & Career", "Tea Culture & Ceremonies",
            "Cinema & TV Shows", "Fashion & Clothing Trends",
            "Sports & Olympics", "Mythology & Folklore",
            "Poetry & Classic Literature", "Regional Dialects & Accents",
            "Gift Giving & Taboos", "Hobbies & Leisure Activities",
            "Housing & Real Estate", "Mobile Apps & Digital Life"
        ]
        selected_category = random.choice(categories)

        return Task(
            description=(
                f"Suggest a single, UNIQUE topic suitable for HSK level '{level}'.\n"
                f"FOCUS DOMAIN: {selected_category} (You MUST choose a topic within this specific domain).\n"
                f"Constraint: You MUST NOT reuse any of these recent topics: [{recent_topics}].\n"
                f"Random Seed: {random_seed}.\n"
                "The topic should be interesting, specific, and culturally relevant.\n"
                "Be creative! Look for unique angles or specific sub-topics rather than generic ones.\n"
                "Output ONLY the topic name (e.g., 'The Art of Tea Making' or 'Mobile Payments in China')."
            ),
            expected_output='A single string representing the topic.',
            agent=agent
        )

    def write_content_task(self, agent, topic, level):
        # Determine target length based on HSK level (increased by ~20%)
        hsk_lengths = {
            "HSK 1": "100-150 words",
            "HSK 2": "150-200 words",
            "HSK 3": "200-400 words",
            "HSK 4": "400-600 words",
            "HSK 5": "700-900 words",
            "HSK 6": "1000-1200 words"
        }
        
        # Default to HSK 3 range if not found, or loose matching
        length = "200-250 words"
        for key, val in hsk_lengths.items():
            if key in level:
                length = val
                break
                
        return Task(
            description=(
                f"Write a comprehensive reading passage (article or story) of approx {length} about '{topic}' following the provided lesson plan. "
                "Ensure the language style and difficulty match the target HSK level defined in the plan.\n\n"
                "IMPORTANT: Write in continuous prose (paragraphs). Do NOT write a dialogue/script.\n"
                "You must output the content in THREE distinct sections:\n"
                "1. **Hanzi Only**: The text written purely in Chinese characters.\n"
                "2. **Pinyin**: The full pinyin transcription of the text.\n"
                "3. **Translation**: The English translation.\n\n"
                "Format as:\n"
                "# Story (Hanzi)\n[Content]\n\n"
                "# Pinyin\n[Content]\n\n"
                "# Translation\n[Content]"
            ),
            expected_output='A reading passage formatted with Hanzi, Pinyin, and Translation sections.',
            agent=agent
        )

    def analyze_language_task(self, agent):
        return Task(
            description=(
                "Analyze the story/dialogue created in the previous task. "
                "You MUST output valid JSON. The structure MUST be:\n"
                "{\n"
                "  \"vocabulary\": [\n"
                "    {\"hanzi\": \"Word\", \"pinyin\": \"pinyin\", \"meaning\": \"meaning\", \"example\": \"Example sentence using the word.\", \"example_pinyin\": \"Pinyin for example.\", \"example_meaning\": \"English translation of example.\"},\n"
                "    ... (select 12-20 key words from the text) ...\n"
                "  ],\n"
                "  \"grammar\": [\n"
                "    {\"pattern\": \"Pattern\", \"explanation\": \"Explanation...\", \"example\": \"Example...\"},\n"
                "    ...more items...\n"
                "  ]\n"
                "}\n"
                "Extract 12-20 key vocabulary words (prioritize new or difficult words) and 3-5 grammar patterns."
            ),
            expected_output='Valid JSON object with vocabulary and grammar arrays.',
            agent=agent
        )

    def create_quiz_task(self, agent):
        return Task(
            description=(
                "Create a diverse set of exercises based on the story and vocabulary. "
                "You MUST output valid JSON with EXACTLY this structure:\n"
                "{\n"
                "  \"exercises\": [\n"
                "    {\n"
                "      \"type\": \"multiple_choice\",\n"
                "      \"question\": \"What did the character order?\",\n"
                "      \"options\": [\"A. Coffee\", \"B. Tea\", \"C. Water\", \"D. Juice\"],\n"
                "      \"answer\": \"A\",\n"
                "      \"explanation\": \"The text says he ordered a coffee.\"\n"
                "    },\n"
                "    {\n"
                "      \"type\": \"fill_blank\",\n"
                "      \"sentence\": \"他去___买咖啡。\",\n"
                "      \"answer\": \"商店\",\n"
                "      \"hint\": \"A place to buy things (shāngdiàn)\",\n"
                "      \"explanation\": \"商店 means store/shop.\"\n"
                "    },\n"
                "    {\n"
                "      \"type\": \"matching\",\n"
                "      \"pairs\": [\n"
                "        {\"hanzi\": \"咖啡\", \"meaning\": \"coffee\"},\n"
                "        {\"hanzi\": \"商店\", \"meaning\": \"store\"},\n"
                "        {\"hanzi\": \"好喝\", \"meaning\": \"delicious (drink)\"}\n"
                "      ]\n"
                "    },\n"
                "    {\n"
                "      \"type\": \"sentence_order\",\n"
                "      \"words\": [\"咖啡\", \"我\", \"喝\", \"想\"],\n"
                "      \"answer\": \"我想喝咖啡\",\n"
                "      \"translation\": \"I want to drink coffee.\"\n"
                "    }\n"
                "  ]\n"
                "}\n\n"
                "CREATE EXACTLY:\n"
                "- 10 multiple_choice questions (reading comprehension)\n"
                "- 5 fill_blank exercises (vocabulary in context)\n"
                "- 1 matching exercise with 5 word pairs\n"
                "- 5 sentence_order exercises (grammar practice)\n"
            ),
            expected_output='Valid JSON object with exercises array containing diverse quiz types.',
            agent=agent
        )

