from google.cloud import texttospeech
from google.oauth2 import service_account
import os

def tts_google_cloud(text, language_code="fr-FR", gender="MALE", credentials_path=None):
    """Synthesizes speech from the input string of text, optionally using specific credentials."""
    if credentials_path and os.path.exists(credentials_path):
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = texttospeech.TextToSpeechClient(credentials=credentials)
        print(f"Using credentials from: {credentials_path}")
    else:
        # Uses Application Default Credentials.
        # See https://cloud.google.com/docs/authentication/application-default-credentials
        client = texttospeech.TextToSpeechClient()
        print("Using Application Default Credentials.")

    synthesis_input = texttospeech.SynthesisInput(text=text)

    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.SsmlVoiceGender[gender.upper()]
    )

    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )

    response = client.synthesize_speech(
        input=synthesis_input, voice=voice, audio_config=audio_config
    )

    with open("output.mp3", "wb") as out:
        out.write(response.audio_content)
    return "output.mp3"

if __name__ == "__main__":
    text = "Bonjour, ceci est un test de synthèse vocale."

    # Example using default credentials (e.g., from GOOGLE_APPLICATION_CREDENTIALS env var)
    print("--- Synthesizing with default credentials ---")
    output_file = tts_google_cloud(text, gender="FEMALE")
    print(f"Audio content written to file: {output_file}")

    # Example using a specific service account file.
    # 1. In Google Cloud Console, create a service account with the "Cloud Text-to-Speech API User" role.
    # 2. Download the JSON key file for that service account.
    # 3. Set the path to your key file below and uncomment the lines.
    # key_file = "/path/to/your/service-account-key.json"
    # print(f"\n--- Synthesizing with credentials from a file ---")
    # output_file_sa = tts_google_cloud(text, credentials_path=key_file)
    # print(f"Audio content written to file: {output_file_sa}")
