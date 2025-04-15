from pydantic import BaseModel
import pyttsx3
from fastapi.responses import FileResponse

app = FastAPI()

class Query(BaseModel):
    text: str

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
