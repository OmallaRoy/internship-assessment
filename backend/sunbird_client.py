import requests
import os
from dotenv import load_dotenv
from mutagen import File as MutagenFile

load_dotenv()

BASE_URL = "https://api.sunbird.ai"  # URL where all API requests are made to
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")

headers = {"Authorization": f"Bearer {API_TOKEN}"}


def transcribe(audio_file):
    audio = MutagenFile(audio_file) # audio_file is the audio file to be processed
    if audio is None:
        return "Error: Unsupported audio format."
    duration = audio.info.length # read duration of the audio file
    if duration > 300:
        return "Error: Audio file exceeds 5 minutes. Please upload a shorter file."

    try:
        filename = os.path.basename(audio_file)
        ext = os.path.splitext(audio_file)[1].lower()
        content_types = { 
            #declare acceptable audio file types and map each format to its correct HTTP content type             
            ".mp3": "audio/mpeg",
            ".wav": "audio/wav",
            ".ogg": "audio/ogg",
            ".m4a": "audio/m4a",
            ".aac": "audio/aac",
        }
        content_type = content_types.get(ext, "audio/mpeg")
        files = {"audio": (filename, open(audio_file, "rb"), content_type)}

        response = requests.post(
            BASE_URL + "/tasks/stt", headers=headers, files=files
        )
        if response.status_code == 200:
            return response.json()["audio_transcription"]
        else:
            return f"Error: {response.status_code} - {response.text}"

    except FileNotFoundError:
        return "Error: Audio file not discovered at the path."
