import speech_recognition as sr # speech to text lib

def record_voice():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    print("🎤 Parle maintenant, j’écoute...")
    with mic as source:
        recognizer.adjust_for_ambient_noise(source)
        audio = recognizer.listen(source)

    print("📡 Transcription en cours...")
    try:
        text = recognizer.recognize_google(audio, language="fr-FR")
        print(f"📝 Tu as dit : {text}")
        return text
    except sr.UnknownValueError:
        print("😕 Je n’ai pas compris.")
    except sr.RequestError as e:
        print(f"🚨 Erreur lors de la requête : {e}")

    return None
