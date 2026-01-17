
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
