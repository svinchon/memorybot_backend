from http.client import HTTPException
from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
import pyttsx3
from fastapi.responses import FileResponse
from gtts import gTTS
import os
import shutil

app = FastAPI()

class Query(BaseModel):
    text: str

# get text response
@app.post("/submit-question")
def get_response(query: Query):
    response = f"Your memory bot says: {query.text}"
    return {"text": response}

#get mp3 from text

@app.post("/tts_pyttsx3")
def tts_pyttsx3(query: Query):
    print(query.text)
    engine = pyttsx3.init()
    # engine.say(query.text)
    # engine.runAndWait()
    engine.save_to_file(query.text, "response_temp.mp3")
    engine.runAndWait()
    # return {"file": "response.mp3"}
    return FileResponse("response_temp.mp3", media_type='audio/mpeg')

@app.post("/tts_gtts")
def tts_gtts(query: Query):
    print(query.text)
    tts = gTTS(query.text, lang='en')
    tts.save("response_gtts.mp3")
    return FileResponse("response_gtts.mp3", media_type='audio/mpeg')

@app.post("/stt")
def stt(file: UploadFile = File(...)):
    #print(query.text)
    if file.content_type != "audio/mpeg":
        raise HTTPException(status_code=400, detail="Invalid file type. Only MP3 files are allowed.")
    try:
        # Create a directory if it doesn't exist
        upload_dir = "uploaded_mp3s"
        os.makedirs(upload_dir, exist_ok=True)

        # Save the file
        file_path = os.path.join(upload_dir, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return {"message": f"Successfully uploaded and saved {file.filename} to {file_path}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving file: {e}")
