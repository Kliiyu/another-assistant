import ollama
from dotenv import load_dotenv
import os

load_dotenv()

def prompt_assistant(prompt: str) -> str:
    host = ollama.Client(os.getenv("OLLAMA_HOST", "http://localhost:11434")) 
    response = host.chat(model=os.getenv("OLLAMA_LLM_MODEL"), messages=[{'role': 'user', 'content': prompt}])
    return response["message"]["content"]

if __name__ == "__main__":
    prompt = "What is the weather like in Oslo?"
    response = prompt_assistant(prompt)
    print(response)
