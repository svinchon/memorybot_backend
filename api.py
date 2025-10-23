
# region "Imports"

# import all needed libraries
import json
import os
import shutil
from datetime import datetime
from http.client import HTTPException
import re

# fastapi libraries
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import JSONResponse, FileResponse, PlainTextResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from pydantic import BaseModel

# google libraries
from gtts import gTTS
import speech_recognition as sr

# local libraries
from infrags_mgr.memory_store import MemoryStore
from infrags_mgr.infrag_store import InfragStore
from infrags_mgr.openai_chatbot import OpenAIChatbot
from infrags_mgr.google_chatbot import GoogleChatbot

# endregion

# region "FastAPI"

fast_api_app = FastAPI()

static_dir = "static"
if os.path.exists(static_dir):
    fast_api_app.mount("/static", StaticFiles(directory=static_dir), name="static")

@fast_api_app.get("/gui", response_class=HTMLResponse)
async def get_web_interface():
    """Sert l'interface web graphique"""
    html_file = "static/index.html"
    if os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    else:
        return HTMLResponse("<h1>Interface non trouvée</h1><p>Le fichier index.html n'existe pas dans le dossier static/</p>")


# endregion

# region "Queries"

class Query(BaseModel):
    text: str
    language: str = "fr-FR"
    voice_type: str

class StoreInfragQuery(BaseModel):
    user_id: str
    user_context: str
    infrag: str
    language: str = "fr-FR"

class UpdateInfragQuery(BaseModel):
    user_id: str
    user_context: str
    infrag_id: str
    new_text: str

class DeleteInfragQuery(BaseModel):
    user_id: str
    user_context: str
    infrag_id: str

class AskQuery(BaseModel):
    user_id: str
    user_context: str
    instructions: str
    question: str

class LLMQuery(BaseModel):
    user_id: str
    instructions: str = ""
    request: str
    language: str = "fr-FR"

class LLMProvidingInfragsQuery(BaseModel):
    user_id: str
    user_context:  str
    instructions: str = ""
    request: str
    language: str = "fr-FR"

# endregion

# region "Instantiations"

store = MemoryStore()
infrag_store = InfragStore()
# chatbot = OpenAIChatbot()
chatbot = GoogleChatbot()

# endregion

# region "Utility Functions"

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

# endregion

# region "Mappings"

# region "Admin"

@fast_api_app.get("/")
def read_root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <meta http-equiv="refresh" content="0; url=/gui">
        <title>Redirection...</title>
    </head>
    <body>
        <p>Redirection vers l'interface... <a href="/gui">Cliquez ici si la redirection ne fonctionne pas</a></p>
    </body>
    </html>
    """)

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

@fast_api_app.get("/debug")
def debug():
    version = get_version()
    gcs_content = get_gcs_content()
    return {
        "message": f"container generated on {version} is ok",
        "timestamp": f"{datetime.now().strftime('%Y-%m-%d@%H-%M-%S')}",
        "gcs": gcs_content,
        "islocal": get_is_local(),
        "llm": chatbot.llm
    }

@fast_api_app.get("/config")
def get_config():
    file_path = "data/config.json"
    with open(file_path, "r") as file:
        file_content = file.read()
        file_content_json = json.loads(file_content)
    return JSONResponse(
        content={"config": file_content_json},
        media_type="application/json; charset=utf-8"
    )

# endregion

# region "v2"

@fast_api_app.post("/v2/infrags/add")
def add_infrag(query: StoreInfragQuery):
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

@fast_api_app.get("/v2/infrags")
def get_infrags():
    file_path = "infrags_mgr/data/infrags.json"
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

@fast_api_app.post("/v2/infrags")
def post_infrags(file: UploadFile = File(...)):
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    infrags_path = "infrags_mgr/data/infrags.json"
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

@fast_api_app.get("/v2/infrags/reload")
def reload_infrags():
    InfragStore.reload_infrags
    return JSONResponse(
        content={"message": "infrags reloaded successfully"},
        media_type="application/json; charset=utf-8"
    )

@fast_api_app.put("/v2/infrags/{infrag_id}")
def update_infrag(infrag_id: str, query: UpdateInfragQuery):
    try:
        # Vérifier que l'ID correspond
        if infrag_id != query.infrag_id:
            raise HTTPException(status_code=400, detail="ID mismatch")

        # Appeler la méthode update_infrag du store
        success = infrag_store.update_infrag(
            infrag_id=query.infrag_id,
            user_id=query.user_id,
            user_context=query.user_context,
            new_text=query.new_text
        )
        infrag_store.reload_infrags()
        infrag_store.rebuild_index()

        if success:
            return {"text": "Fragment mis à jour avec succès!"}
        else:
            raise HTTPException(status_code=404, detail="Fragment non trouvé")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la mise à jour: {str(e)}")

@fast_api_app.delete("/v2/infrags/{infrag_id}")
def delete_infrag(infrag_id: str, user_id: str, user_context: str):
    try:
        #user_id = request.args.get('user_id')
        #user_context = request.args.get('user_context')
        # Appeler la méthode delete_infrag du store
        #print(f"Deleting infrag with ID: {infrag_id}, user_id: {user_id}, user_context: {user_context}")
        success = infrag_store.delete_infrag(
            infrag_id=infrag_id,
            user_id=user_id,
            user_context=user_context
        )
        if success:
            return {"text": "Fragment supprimé avec succès!"}
        else:
            raise HTTPException(status_code=404, detail="Fragment non trouvé")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la suppression: {str(e)}")

@fast_api_app.get("/v2/infrags/detailed")
def get_infrags_detailed(user_id: str = None, user_context: str = None):
    try:
        # Appeler une méthode pour récupérer les fragments avec filtres
        infrags = infrag_store.get_infrags_filtered(user_id=user_id, user_context=user_context)
        return JSONResponse(
            content={"infrags": infrags},
            media_type="application/json; charset=utf-8"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {str(e)}")

# "/ask-llm" POST mapping
@fast_api_app.post("/v2/ask-llm")
def askLLM(query: LLMQuery):
    print("starting REST service ask-llm")
    print(f"language: {query.language}")
    response = "je ne sais rien, mais je dirai tout"
    if query.language == "en-US":
        query.instructions += "\nPlease answer in English."
    response = chatbot.askLLM(
        query.user_id,
        query.instructions,
        query.request,
        query.language,
    )
    return JSONResponse(
        content={ "text": response },
        media_type="application/json; charset=utf-8"
    )

# "/ask-llm-providing-infrags" POST mapping
@fast_api_app.post("/v2/ask-llm-providing-infrags")
def askLLMProvidingInfrags(query: LLMProvidingInfragsQuery):
    print("starting REST service ask-llm-providing-infrags")
    response = "je ne sais rien, mais je dirai tout"
    infrags = infrag_store.search_infrags(
        query.user_id,
        query.user_context,
        query.request,
        query.language,
    )
    context = "\n".join(
      [f"- {m['text']} (stocké le {m['storage_date']})" for m in infrags]
    )
    instructions = query.instructions
    instructions += f"\nVoici les éléments d'information pertinents :\n{context}"
    print(instructions)
    if (query.language == "en-US"):
        instructions += f"\nPlease answer in English."
    response = chatbot.queryInfrags(
        query.request,
        instructions,
        infrags,
        language=query.language
    )
    response = response.replace("**", "")
    return JSONResponse(
        content={ "text": response },
        media_type="application/json; charset=utf-8"
    )

# endregion

# region "v1"

@fast_api_app.post("/v1/ask")
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

@fast_api_app.post("v1/store")
def add_memory(query: Query):
    ts = datetime.now().strftime("%Y-%m-%d")
    store.add_memory(query.text, ts) # add user_id and user_context
    return {"text": "Memory added successfully!"}

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
        query.question,
        query.language,
    )
    # call the queryInfrags method of the chatbot object
    # with the question, instructions and the list of information fragments
    # to get the answer to the question
    # this will return the answer to the question
    response = chatbot.queryInfrags(
        query.question,
        query.instructions,
        infrags,
        query.language
    )
    # return the answer to the question in a JSON object looking like {"text": "ceci est un test"}
    responseJson = {"text": response}
    return JSONResponse(
        content=responseJson,
        media_type="application/json; charset=utf-8"
    )

# endregion

# region "Speech to Text and Text to Speech"

@fast_api_app.post("/text-to-speech")
def tts_gtts(query: Query):
    print("starting REST service text-to-speech")
    print("language: ", query.language)
    ts = datetime.now().strftime("%Y-%m-%d@%H-%M-%S")
    upload_dir = "uploaded_files"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"response_{ts}.mp3")
    tts = gTTS(query.text, lang=query.language, slow=False)
    tts.save(file_path)
    size_in_bytes = os.path.getsize(file_path)
    print(f"File saved at {file_path} with size {size_in_bytes} bytes")
    return FileResponse(file_path, media_type='audio/mpeg')

# "/speech-to-text URL mapping (returns text in JSON)
@fast_api_app.post("/speech-to-text")
def stt(
    file: UploadFile = File(...),
    language: str = Form(...)
):
    print("starting REST service speech-to-text")
    print("language: ", language)
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
        text = recognizer.recognize_google(
            audio, language=language
        )
    except sr.UnknownValueError:
        text = "Could not understand the audio."
    except sr.RequestError as e:
        text = f"request error: {e}"
    except Exception as e:
        text = f"Error saving file: {e}"
    return {"text": text}

# endregion

# endregion

# if python script is run directly, run the following code
if __name__ == "__main__":
    # store.add_memory("text", "2023-10-01")
    q = Query(text="qui suis-je ?")
    print(ask(q))
