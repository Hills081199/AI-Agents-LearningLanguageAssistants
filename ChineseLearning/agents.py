from crewai import Agent
from crewai.tools import BaseTool

class ChineseLearningAgents:
    def lesson_planner_agent(self):
        return Agent(
            role='Senior Chinese Curriculum Developer',
            goal='Create a structured lesson plan for a specific topic and HSK level',
            backstory='Expert in teaching Chinese as a second language (CSL). You know exactly what vocabulary and grammar patterns fit each HSK level.',
            verbose=True,
            memory=True
        )

    def content_writer_agent(self):
        return Agent(
            role='Chinese Content Writer',
            goal='Write engaging and natural short stories or dialogues in Chinese based on a lesson plan',
            backstory='A creative writer who specializes in grading reading materials for language learners.',
            verbose=True,
            memory=True
        )

    def linguist_agent(self):
        return Agent(
            role='Chinese Linguist',
            goal='Analyze text to extract vocabulary and explain grammar points',
            backstory='You love analyzing sentence structures and have deep knowledge of Chinese grammar and Pinyin.',
            verbose=True,
            memory=True
        )

    def examiner_agent(self):
        return Agent(
            role='HSK Examiner',
            goal='Create comprehension quizzes based on the provided text',
            backstory='You create official HSK practice tests. You know how to test understanding without being confusing.',
            verbose=True,
            memory=True
        )
