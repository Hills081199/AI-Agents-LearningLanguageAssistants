
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
