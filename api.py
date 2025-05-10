# main file / class
# instantiated by uvicorn at statup

# region "Imports"

# import all needed libraries
import json
import os
import shutil
from datetime import datetime
from http.client import HTTPException
import re

# fastapi libraries
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse

from pydantic import BaseModel

# google libraries
from gtts import gTTS
import speech_recognition as sr

# local libraries
from infragsmgr.memory_store import MemoryStore
from infragsmgr.infrag_store import InfragStore
from infragsmgr.chatbot import Chatbot

# endregion

# region "FastAPI"
# usage of the FastAPI framework to expose a REST API
# endregion
fast_api_app = FastAPI()

# region "Query"
# first type of object used to pass information to the API
# JSON object looking like {"text": "ceci est un test"}
# endregion
class Query(BaseModel):
    text: str

# region "StoreQuery"
# second type of object used to pass information to the API
# (to store an "information fragment", for instance a memory)
# JSON object looking like
# {
# "user_id": "toto@gmail.com",
# "user_context": "souvenirs",
# "infrag": "un jour je suis né"
# }
# endregion
class StoreQuery(BaseModel):
    user_id: str
    user_context: str
    infrag: str

# region "AskQuery"
# third type of object used to pass information to the API
# (to ask a question)
# JSON object looking like
# {
# "user_id": "toto@gmail.com",
# "user_context": "souvenirs",
# "infinstructionds":
# "un jour je suis né"
# }
# endregion
class AskQuery(BaseModel):
    user_id: str
    user_context: str
    instructions: str
    question: str

class LLMQuery(BaseModel):
    user_id: str
    instructions: str
    request: str

class LLMProvidingInfragsQuery(BaseModel):
    user_id: str
    user_context:  str
    instructions: str
    request: str

# region instantiation
# instantiate the memory store (defined in memories_management/memory_store.py)
# instantiate the infrag store (defined in memories_management/infrag_store.py)
# instantiate the chatbot (defined in memories_management/chatbot.py)
# endregion
store = MemoryStore()
infrag_store = InfragStore()
chatbot = Chatbot()

def get_version():
    try:
        with open("version.txt", "r") as version_file:
            version = version_file.read().strip()
    except FileNotFoundError:
        version = "version.txt not found"
    except Exception as e:
        version = f"Error reading version.txt: {e}"
    return version

def get_is_local():
    islocal_path = "islocal.txt"
    if os.path.exists(islocal_path) and os.path.isfile(islocal_path):
        return True
    else:
        return False

def get_gcs_content():
    # Check if the /gcs folder exists and list its content
    gcs_path = "/gcs"
    if os.path.exists(gcs_path) and os.path.isdir(gcs_path):
        try:
            gcs_content = os.listdir(gcs_path)
        except Exception as e:
            gcs_content = f"Error listing /gcs content: {e}"
    else:
        gcs_content = "Folder /gcs does not exist"
    return gcs_content

# "/" GET mapping
@fast_api_app.get("/")
def read_root():
    version = get_version()
    return {
        "message": f"container generated on {version} is ok",
        "timestamp": f"{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}"
    }

# "/readme" GET mapping
@fast_api_app.get("/readme", response_class=PlainTextResponse)
def readme():
    try:
        with open("readme.txt", "r") as readme_file:
            readme = readme_file.read().strip()
    except FileNotFoundError:
        readme = "readme.txt not found"
    except Exception as e:
        readme = f"Error reading readme.txt: {e}"
    return readme

# "/debug" GET mapping
@fast_api_app.get("/debug")
def debug():
    version = get_version()
    gcs_content = get_gcs_content()
    return {
        "message": f"container generated on {version} is ok",
        "timestamp": f"{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}",
        "gcs": gcs_content,
        "islocal": get_is_local()
    }

# "/infrags" GET mapping
@fast_api_app.get("/infrags")
def get_infrags():
    file_path = "infragsmgr/data/infrags.json"
    if (get_is_local() != True):
        file_path = "/gcs/voiceagent/infrags.json"
    with open(file_path, "r") as infrags_file:
        infrags = infrags_file.read()
        infrags = re.sub(r"\n *", "", infrags)
        infrags = json.loads(infrags)
    return JSONResponse(
        content={"infrags": infrags},
        media_type="application/json; charset=utf-8"
    )

# "/infrags" POST mapping
@fast_api_app.post("/infrags")
def post_infrags(file: UploadFile = File(...)):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    infrags_path = "infragsmgr/data/infrags.json"
    if (get_is_local() == False):
        infrags_path = "/gcs/voiceagent/infrags.json"
    infrags_backup_path = infrags_path + f".{ts}.bak"
    shutil.copy(infrags_path, infrags_backup_path)
    #shutil.delete(infrags_path)
    with open(infrags_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return JSONResponse(
        content={"message": "File uploaded successfully"},
        media_type="application/json; charset=utf-8"
    )

# TODO: add reload infrags api
@fast_api_app.get("/reload-infrags")
def reload_infrags():
    InfragStore.reload_infrags
    return JSONResponse(
        content={"message": "infrags reloaded successfully"},
        media_type="application/json; charset=utf-8"
    )

# "/ask" POST mapping"
@fast_api_app.post("/ask")
def askV1(query: Query):
    response = "je sais pas"
    question = query.text
    memories = store.search_memories(query.text) # add user_id and user_context
    response = chatbot.ask(question, memories) # add instructions
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

# "/store" POST mapping
@fast_api_app.post("/store")
def add_memory(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d")
    store.add_memory(query.text, ts) # add user_id and user_context
    return {"text": "Memory added successfully!"}

# "/v2/ask" POST mapping
@fast_api_app.post("/v2/ask")
def askV2(query: AskQuery):
    print("starting ask V2")
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
    # return the answer to the question in a JSON object looking like {"text": "ceci est un test"}
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

# "/v2/store" POST mapping
@fast_api_app.post("/v2/store")
def add_infrag(query: StoreQuery):
    # create a timestamp with the current date
    ts = datetime.now().strftime("%Y-%m-%d")
    # call the add_infrag of the infrag_store object with the user_id, user_context, infrag (infomation fragment) and a timestamp
    infrag_store.add_infrag(
        user_id=query.user_id,
        user_context=query.user_context,
        text=query.infrag,
        date=ts
    )
    return {"text": "Information fragment added successfully!"}

# "/text-to-speech" POST mapping (returns mp3)
@fast_api_app.post("/text-to-speech")
def tts_gtts(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"response_{ts}.mp3")
    tts = gTTS(query.text, lang='fr')
    tts.save(file_path)
    return FileResponse(file_path, media_type='audio/mpeg')

# "/speech-to-text URL mapping (returns text in JSON)
@fast_api_app.post("/speech-to-text")
def stt(file: UploadFile = File(...)):
    text = ""
    try:
        ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
        if (file.content_type != "audio/mpeg"):
            text = "Invalid file type"
        upload_dir = "uploaded_files"
        os.makedirs(upload_dir, exist_ok=True)
        file_ext = os.path.splitext(file.filename)[1]
        file_filename = os.path.splitext(file.filename)[0]
        # print(f"file_ext: {file_ext}")
        # print(f"file.filename: {file.filename}")
        file_path = os.path.join(upload_dir, f"{file_filename}_{ts}{file_ext}")
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        recognizer = sr.Recognizer()
        with sr.AudioFile(file_path) as source:
            audio = recognizer.record(source)
        text = recognizer.recognize_google(audio, language="fr-FR")
    except sr.UnknownValueError:
        text = "Could not understand the audio."
    except sr.RequestError as e:
        text = f"request error: {e}"
    except Exception as e:
        text = f"Error saving file: {e}"
    return {"text": text}

# "/ask-llm" POST mapping
@fast_api_app.post("/ask-llm")
def askLLM(query: LLMQuery):
    print("starting REST service ask-llm")
    response = "je ne sais rien, mais je dirai tout"
    response = chatbot.askLLM(
        query.user_id,
        query.instructions,
        query.request,
    )
    return JSONResponse(
        content={ "text": response },
        media_type="application/json; charset=utf-8"
    )

# "/ask-llm-providing-infrags" POST mapping
@fast_api_app.post("/ask-llm-providing-infrags")
def askLLMProvidingInfrags(query: LLMProvidingInfragsQuery):
    print("starting REST service ask-llm-providing-infrags")
    response = "je ne sais rien, mais je dirai tout"
    infrags = infrag_store.search_infrags(
        query.user_id,
        query.user_context,
        query.request
    )
    context = "\n".join(
      [f"- {m['text']} (socké le {m['storage_date']})" for m in infrags]
    )
    instructions = query.instructions
    instructions += f"\nVoici les éléments d'information pertinents :\n{context}"
    response = chatbot.queryInfrags(
        query.request,
        query.instructions,
        infrags
    )
    return JSONResponse(
        content={ "text": response },
        media_type="application/json; charset=utf-8"
    )

# if python script is run directly, run the following code
if __name__ == "__main__":
    # store.add_memory("text", "2023-10-01")
    q = Query(text="qui suis-je ?")
    print(ask(q))
