import ollama

def prompt_assistant(prompt: str) -> str:
    response = ollama.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
    return response["message"]["content"]
