# main file / class
# instantiated by uvicorn at statup

# import all needed libraries
import os
import shutil
from datetime import datetime
from http.client import HTTPException

# fastapi libraries
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse

from pydantic import BaseModel

# google libraries
from gtts import gTTS
import speech_recognition as sr

# local libraries
from memories_management.memory_store import MemoryStore
from memories_management.infrag_store import InfragStore
from memories_management.chatbot import Chatbot

# usage of the FastAPI framework to expose a REST API
fast_api_app = FastAPI()

# first type of object used to pass information to the API
# JSON object looking like {"text": "ceci est un test"}
class Query(BaseModel):
    text: str

# second type of object used to pass information to the API
# (to store an "information fragment", for instance a memory)
# JSON object looking like
# {
# "user_id": "toto@gmail.com",
# "user_context": "souvenirs",
# "infrag": "un jour je suis né"
# }
class StoreQuery(BaseModel):
    user_id: str
    user_context: str
    infrag: str

# third type of object used to pass information to the API
# (to ask a question)
# JSON object looking like
# {
# "user_id": "toto@gmail.com",
# "user_context": "souvenirs",
# "infinstructionds":
# "un jour je suis né"
# }
class AskQuery(BaseModel):
    user_id: str
    user_context: str
    instructions: str
    question: str

# instantiate the memory store (defined in memories_management/memory_store.py)
# instantiate the infrag store (defined in memories_management/infrag_store.py)
# instantiate the chatbot (defined in memories_management/chatbot.py)
store = MemoryStore()
infrag_store = InfragStore()
chatbot = Chatbot()

# define what to do by default when the root URL is called
@fast_api_app.get("/")
def read_root():
    return {
        "message": "container ok",
        "timestamp": f"{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}"
    }

# define what to do when the /ask URL is called
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

# define what to do when the /store URL is called
@fast_api_app.post("/store")
def add_memory(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d")
    store.add_memory(query.text, ts) # add user_id and user_context
    return {"text": "Memory added successfully!"}

# define what to do when the /v2/ask URL is called
@fast_api_app.post("/v2/ask") # modifié
def ask(query: AskQuery):
    # default response
    response = "je ne sais rien, mais je dirai tout"
    # call the search_infrags of the infrag_store object
    # with the user_id, user_context and question
    # to get the information fragments
    # that are relevant to the question
    # this will return a list of information fragments
    # that are relevant to the question
    infrags = infrag_store.search_infrags(
        query.user_id,
        query.user_context,
        query.question
    )
    # call the queryInfrags method of the chatbot object
    # with the question, instructions and the list of information fragments
    # to get the answer to the question
    # this will return the answer to the question
    response = chatbot.queryInfrags(
        query.question,
        query.instructions,
        infrags
    )
    # return the answer to the question
    # in a JSON object looking like {"text": "ceci est un test"}
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

# define what to do when the /v2/store URL is called
@fast_api_app.post("/v2/store") # modifié
def add_infrag(query: StoreQuery):
    # create a timestamp with the current date
    ts = datetime.now().strftime("%Y-%m-%d")
    # call the add_infrag of the infrag_store object
    # with the user_id, user_context, infrag (infomation fragment)
    # and a timestamp
    infrag_store.add_infrag(
        user_id=query.user_id,
        user_context=query.user_context,
        text=query.infrag,
        date=ts
    )
    return {"text": "Information fragment added successfully!"}

# define what to do when the /text-to-speech URL is called
# this function is used to convert text to speech (mp3)
@fast_api_app.post("/text-to-speech")
def tts_gtts(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"response_{ts}.mp3")
    tts = gTTS(query.text, lang='fr')
    tts.save(file_path)
    return FileResponse(file_path, media_type='audio/mpeg')

# define what to do when the /speech-to-text URL is called
# this function is used to convert an audio file (mp3) to text
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

# defined what to do this file is run directly
# (not used in production, but useful for testing)
if __name__ == "__main__":
    # store.add_memory("text", "2023-10-01")
    q = Query(text="qui suis-je ?")
    print(ask(q))
