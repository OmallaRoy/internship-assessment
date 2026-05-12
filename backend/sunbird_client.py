import requests
import os
from dotenv import load_dotenv
from mutagen import File as MutagenFile

load_dotenv()

BASE_URL = "https://api.sunbird.ai"  # URL where all API requests are made to
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")

headers = {"Authorization": f"Bearer {API_TOKEN}"}
content_types = {
    # declare acceptable audio file types and map each format to its
    # correct HTTP content type
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/m4a",
    ".aac": "audio/aac",
}


# function responsible for the transcribe logic
def transcribe(audio_file):
    audio = MutagenFile(
        audio_file
    )  # audio_file is the audio file to be processed
    if audio is None:
        return "Unsupported audio format."
    duration = audio.info.length  # read duration of the audio file
    if duration > 300:
        return "Audio file exceeds 5 minutes. Please upload a shorter file."

    try:
        filename = os.path.basename(audio_file)
        ext = os.path.splitext(audio_file)[1].lower()
        if ext not in content_types:
            return "Unsupported file format. Please upload MP3, WAV, OGG, M4A or AAC."

        content_type = content_types[ext]
        files = {"audio": (filename, open(audio_file, "rb"), content_type)}

        response = requests.post(
            BASE_URL + "/tasks/stt", headers=headers, files=files
        )
        if response.status_code == 200:
            return response.json()["audio_transcription"]
        else:
            return f"Error: {response.status_code} - {response.text}"

    except FileNotFoundError:
        return "Audio file not discovered at the path."


# function responsible for the transcribe logic
def summarise(text):

    try:

        response = requests.post(
            BASE_URL + "/tasks/sunflower_simple",
            headers=headers,
            data={"instruction": "Summarise the following text: " + text},
            timeout=180,
        )
        if response.status_code == 200:
            return response.json()["response"]
        elif response.status_code == 504:
            return "Error: Server timeout. Please try again."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"


# function responsible for the translate logic
def translate(text, language):
    try:
        response = requests.post(
            BASE_URL + "/tasks/sunflower_simple",
            headers=headers,
            data={
                "instruction": "Translate the following text to "
                + language
                + ":"
                + text
            },
            timeout=180,
        )
        if response.status_code == 200:
            return response.json()["response"]
        elif response.status_code == 504:
            return "Error: Server timeout. Please try again."
        else:
            return f"Error: {response.status_code} - {response.text}"
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again later."
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"

