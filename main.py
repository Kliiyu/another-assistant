from fastapi import FastAPI, Form, File, UploadFile
from fastapi.responses import JSONResponse
from orchestrator import orchestrate
from memory.memory import add_to_memory
import speech_recognition as sr
import tempfile
import os
import shutil

app = FastAPI()

@app.post("/api/prompt")
async def handle_prompt(prompt: str = Form(...)):
    add_to_memory(prompt)
    result = orchestrate(prompt)
    add_to_memory(result)
    return JSONResponse(content={"response": result})

def transcribe(path: str) -> str:
    """_summary_
    ## Transcribe text to be intereted by assistant
    Args:
        path (str): File to transcribe (wav)
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(path) as source:
        audio_data = recognizer.record(source)
        try:
            return recognizer.recognize_google(audio_data)
        except sr.UnknownValueError:
            return "Unable to recognize speech"
        except sr.RequestError as e:
            return f"Speech recognition service error: {e}"

@app.post("/api/file")
async def handle_file(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_file:
        shutil.copyfileobj(file.file, temp_file)
        temp_file_path = temp_file.name
    
    try:
        text_result = transcribe(temp_file_path)
        add_to_memory(text_result)
        result = orchestrate(text_result)
        add_to_memory(result)
        return JSONResponse(content={"response": result})
    finally:
        os.unlink(temp_file_path)
