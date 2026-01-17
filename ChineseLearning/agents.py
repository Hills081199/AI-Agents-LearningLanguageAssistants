from crewai import Agent
from crewai.tools import BaseTool

# Language Configuration for Multi-Language Support
LANGUAGE_CONFIG = {
    "chinese": {
        "name": "Chinese",
        "native_name": "中文",
        "levels": ["HSK 1", "HSK 2", "HSK 3", "HSK 4", "HSK 5", "HSK 6"],
        "level_system": "HSK",
        "tts_code": "zh-CN",
        "has_romanization": True,
        "romanization_name": "Pinyin",
        "script_direction": "ltr",
        "example_topics": [
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
            "Tea Culture & Ceremonies", "Cinema & TV Shows"
        ]
    },
    "english": {
        "name": "English",
        "native_name": "English",
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "level_system": "CEFR",
        "tts_code": "en-US",
        "has_romanization": False,
        "romanization_name": None,
        "script_direction": "ltr",
        "example_topics": [
            "Daily Routines & Habits", "Travel & Tourism",
            "Work & Career", "Technology & Internet",
            "Health & Fitness", "Food & Cooking",
            "Sports & Hobbies", "Music & Entertainment",
            "News & Current Events", "Environment & Climate",
            "Education & Learning", "Shopping & Fashion",
            "Relationships & Family", "Holidays & Celebrations",
            "Business & Finance", "Science & Innovation",
            "Arts & Culture", "Social Media & Digital Life",
            "Movies & TV Series", "Books & Literature",
            "History & Heritage", "Nature & Wildlife",
            "City Life & Urban Culture", "Countryside & Rural Life",
            "Public Transport & Commuting", "Banking & Personal Finance"
        ]
    },
    "spanish": {
        "name": "Spanish",
        "native_name": "Español",
        "levels": ["A1", "A2", "B1", "B2", "C1", "C2"],
        "level_system": "CEFR",
        "tts_code": "es-ES",
        "has_romanization": False,
        "romanization_name": None,
        "script_direction": "ltr",
        "example_topics": [
            "La vida cotidiana", "Viajes y turismo",
            "Trabajo y carrera", "Tecnología e internet",
            "Salud y bienestar", "Comida y gastronomía",
            "Deportes y aficiones", "Música y entretenimiento",
            "Noticias y actualidad", "Medio ambiente y clima",
            "Educación y aprendizaje", "Compras y moda",
            "Relaciones y familia", "Fiestas y celebraciones",
            "Negocios y finanzas", "Ciencia e innovación",
            "Arte y cultura", "Redes sociales y vida digital",
            "Cine y series", "Libros y literatura",
            "Historia y patrimonio", "Naturaleza y vida silvestre",
            "Cultura latinoamericana", "Tradiciones españolas",
            "Flamenco y música tradicional", "Fútbol y deportes populares"
        ]
    }
}

def get_language_config(language: str) -> dict:
    """Get configuration for a specific language."""
    return LANGUAGE_CONFIG.get(language.lower(), LANGUAGE_CONFIG["chinese"])

def get_supported_languages() -> list:
    """Get list of all supported languages with their configs."""
    return [
        {
            "code": code,
            "name": config["name"],
            "native_name": config["native_name"],
            "levels": config["levels"],
            "level_system": config["level_system"]
        }
        for code, config in LANGUAGE_CONFIG.items()
    ]


class LanguageLearningAgents:
    """Multi-language learning agents supporting Chinese, English, and Spanish."""
    
    def __init__(self, language: str = "chinese"):
        self.language = language.lower()
        self.config = get_language_config(self.language)
        self.lang_name = self.config["name"]
        self.level_system = self.config["level_system"]
    
    def lesson_planner_agent(self):
        return Agent(
            role=f'Senior {self.lang_name} Curriculum Developer',
            goal=f'Create a structured lesson plan for a specific topic and {self.level_system} level',
            backstory=f'Expert in teaching {self.lang_name} as a second language. You know exactly what vocabulary and grammar patterns fit each {self.level_system} level.',
            verbose=True,
            memory=True
        )

    def content_writer_agent(self):
        return Agent(
            role=f'{self.lang_name} Content Writer',
            goal=f'Write engaging and natural short stories or dialogues in {self.lang_name} based on a lesson plan',
            backstory=f'A creative writer who specializes in graded reading materials for {self.lang_name} language learners.',
            verbose=True,
            memory=True
        )

    def linguist_agent(self):
        if self.language == "chinese":
            backstory = f'You love analyzing sentence structures and have deep knowledge of {self.lang_name} grammar and Pinyin.'
        else:
            backstory = f'You love analyzing sentence structures and have deep knowledge of {self.lang_name} grammar, vocabulary, and pronunciation.'
        
        return Agent(
            role=f'{self.lang_name} Linguist',
            goal=f'Analyze text to extract vocabulary and explain grammar points in {self.lang_name}',
            backstory=backstory,
            verbose=True,
            memory=True
        )

    def examiner_agent(self):
        return Agent(
            role=f'{self.lang_name} Examiner',
            goal=f'Create comprehensive quizzes for {self.lang_name} learners',
            backstory=f'Specialist in {self.lang_name} testing and assessment. You know how to create fair but challenging questions.',
            verbose=True,
            memory=True
        )

    def writing_assessor_agent(self):
        return Agent(
            role=f'Senior {self.lang_name} Writing Instructor',
            goal=f'Evaluate {self.lang_name} writing submissions and provide detailed feedback',
            backstory=f'Expert in {self.lang_name} language instruction with extensive experience in academic writing assessment. You believe in providing constructive feedback that helps students improve specific skills.',
            verbose=True,
            memory=True
        )


# Backwards compatibility - keep the old class name as alias
class ChineseLearningAgents(LanguageLearningAgents):
    """Backwards compatible alias for Chinese-only usage."""
    def __init__(self):
        super().__init__(language="chinese")
