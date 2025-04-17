import os
import shutil
from datetime import datetime

from http.client import HTTPException
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

from pydantic import BaseModel

from fastapi.responses import FileResponse
from gtts import gTTS

import speech_recognition as sr

from memories_management.memory_store import MemoryStore
from memories_management.chatbot import Chatbot
from datetime import datetime

app = FastAPI()

class Query(BaseModel):
    text: str

store = MemoryStore()
chatbot = Chatbot()

@app.post("/ask")
def ask(query: Query):
    response = "je sais pas"
    question = query.text
    memories = store.search_memories(query.text)
    response = chatbot.ask(question, memories)
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

@app.post("/store")
def add_memory(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d")
    store.add_memory(query.text, ts)
    return {"text": "Memory added successfully!"}

@app.post("/text-to-speech")
def tts_gtts(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"response_{ts}.mp3")
    tts = gTTS(query.text, lang='fr')
    tts.save(file_path)
    return FileResponse(file_path, media_type='audio/mpeg')

@app.post("/speech-to-text")
def stt(file: UploadFile = File(...)):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    if file.content_type != "audio/mpeg":
        raise HTTPException(status_code=400, detail="Invalid file type.")
    try:
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1]
        file_filename = os.path.splitext(file.filename)[0]
        file_path = os.path.join(upload_dir, f"{file_filename}_{ts}.{file_ext}")
        with open(file_path, "wb") as buffer: shutil.copyfileobj(file.file, buffer)
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source: audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="fr-FR")
        return {"text": text}
    except sr.UnknownValueError:
            print("Impossible de comprendre l'audio.")
    except sr.RequestError as e:
            print("Erreur de requête Google:", e)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")

if __name__ == "__main__":
    # store.add_memory("text", "2023-10-01")
    q = Query(text="qui suis-je ?")
    print(ask(q))
