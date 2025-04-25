import os
import shutil
from datetime import datetime

from http.client import HTTPException
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from gtts import gTTS
import speech_recognition as sr

from memories_management.memory_store import MemoryStore
from memories_management.infrag_store import InfragStore
from memories_management.chatbot import Chatbot
from datetime import datetime

fast_api_app = FastAPI()

class Query(BaseModel):
    text: str

class StoreQuery(BaseModel):
    user_id: str
    user_context: str
    infrag: str

class AskQuery(BaseModel):
    user_id: str
    user_context: str
    instructions: str
    question: str

store = MemoryStore()
infrag_store = InfragStore()
chatbot = Chatbot()

@fast_api_app.get("/")
def read_root():
    return {
        "message": "container ok",
        "timestamp": f"{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}"
    }

@fast_api_app.post("/ask")
def ask(query: Query):
    response = "je sais pas"
    question = query.text
    memories = store.search_memories(query.text) # add user_id and user_context
    response = chatbot.ask(question, memories) # add instructions
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

@fast_api_app.post("/store")
def add_memory(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d")
    store.add_memory(query.text, ts) # add user_id and user_context
    return {"text": "Memory added successfully!"}

@fast_api_app.post("/v2/ask") # modifié
def ask(query: AskQuery):
    response = "je ne sais rien, mais je dirai tout"
    infrags = infrag_store.search_infrags(
        query.user_id,
        query.user_context,
        query.question
    )
    response = chatbot.queryInfrags(
        query.question,
        query.instructions,
        infrags
    )
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

@fast_api_app.post("/v2/store") # modifié
def add_infrag(query: StoreQuery):
    ts = datetime.now().strftime("%Y-%m-%d")
    infrag_store.add_infrag(
        query.user_id,
        query.user_context,
        query.infrag,
        ts
    )
    return {"text": "Infrag added successfully!"}

@fast_api_app.post("/text-to-speech")
def tts_gtts(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"response_{ts}.mp3")
    tts = gTTS(query.text, lang='fr')
    tts.save(file_path)
    return FileResponse(file_path, media_type='audio/mpeg')

@fast_api_app.post("/speech-to-text")
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
