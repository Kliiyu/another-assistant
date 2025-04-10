import ollama

def prompt_assistant(prompt: str) -> str:
    host = ollama.Client("https://ai.iktim.no")
    response = host.chat(model='gemma3:12b-it-q4_K_M', messages=[{'role': 'user', 'content': prompt}])
    return response["message"]["content"]

if __name__ == "__main__":
    prompt = "What is the weather like in Oslo?"
    response = prompt_assistant(prompt)
    print(response)
