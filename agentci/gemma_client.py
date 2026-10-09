
import ollama

MODEL_NAME = "gemma4:e2b"


def suggest_fix(task_description, buggy_code):
    """Ask Gemma to suggest a fix without executing its output."""
    prompt = f"""
You are helping with a code repair task.

Task:
{task_description}

Current code:
{buggy_code}

Explain the bug and provide the complete corrected code.
Do not claim the fix has been tested.
"""

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}],
    )

    return response["message"]["content"]
