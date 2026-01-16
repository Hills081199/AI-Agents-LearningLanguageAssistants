# HSK Content Factory (Chinese Learning Crew)

This project uses CrewAI to automatically generate Chinese learning lessons (Stories, Vocabulary, Grammar, Quizzes) tailored to specific HSK levels.

## Agents

1.  **Lesson Planner**: Designs the curriculum.
2.  **Content Writer**: Writes the story/dialogue.
3.  **Linguist**: Analyzes language and grammar.
4.  **Examiner**: Creates a quiz.

## Usage

1.  **Install Requirements** (if not already installed):
    ```bash
    pip install -r requirements.txt
    ```

2.  **Run the Generator**:
    ```bash
    # Default: "My First Trip to Beijing" (HSK 2)
    python main.py 
    
    # Custom Topic and Level
    python main.py "Ordering Coffee" "HSK 1"
    ```

3.  **Output**:
    -   Check `output/` folder for the generated Markdown lesson.
