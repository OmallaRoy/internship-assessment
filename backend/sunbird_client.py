import requests
import os
from dotenv import load_dotenv
from mutagen import File as MutagenFile

load_dotenv()


# Exception classes
class TranscriptionError(Exception):
    pass


class SummarisationError(Exception):
    pass


class TranslationError(Exception):
    pass


class TextToSpeechError(Exception):
    pass


BASE_URL = "https://api.sunbird.ai"  # URL where all API requests are made to
API_TOKEN = os.getenv("SUNBIRD_API_TOKEN")

headers = {"Authorization": f"Bearer {API_TOKEN}"}
content_types = {
    # declare acceptable audio file types and map each format to its
    # correct HTTP content type
    ".mp3": "audio/mpeg",
    ".wav": "audio/wav",
    ".ogg": "audio/ogg",
    ".m4a": "audio/mp4",  # m4a uses audio/mp4 as its standard MIME type
    ".aac": "audio/aac",
}

# mapping each language to its specific speaker id
speaker_ids = {
    "Luganda": 248,
    "Runyankole": 243,
    "Ateso": 242,
    "Lugbara": 245,
    "Acholi": 241,
}


# function responsible for the transcribe logic
def transcribe(audio_file):

    audio = MutagenFile(
        audio_file
    )  # audio_file is the audio file to be processed
    if audio is None:
        raise TranscriptionError("Unsupported audio format.")
    duration = audio.info.length  # read duration of the audio file
    if duration > 300:
        raise TranscriptionError(
            "Audio file exceeds 5 minutes. Please upload a shorter audio file"
        )

    try:
        filename = os.path.basename(audio_file)
        ext = os.path.splitext(audio_file)[1].lower()
        if ext not in content_types:
            raise TranscriptionError(
                "Unsupported file format. Please upload MP3, WAV, OGG, M4A or AAC."
            )

        content_type = content_types[ext]
        files = {"audio": (filename, open(audio_file, "rb"), content_type)}

        response = requests.post(
            BASE_URL + "/tasks/stt", headers=headers, files=files, timeout=300
        )
        if response.status_code == 200:
            return response.json()[
                "audio_transcription"
            ]  # return the response and get the audio transcription text in dictionary
        else:
            raise TranscriptionError(
                f"Transcription failed with status {response.status_code}."
            )

    except FileNotFoundError:
        raise TranscriptionError("Audio file not found.")


# function responsible for the summarise logic
def summarise(text):

    try:

        response = requests.post(
            BASE_URL + "/tasks/sunflower_simple",
            headers=headers,
            data={"instruction": "Summarise the following text: " + text},
            timeout=300,
        )
        if response.status_code == 200:
            return response.json()[
                "response"
            ]  # return the response and get the response value(summarised text) in dictionary
        elif response.status_code == 504:
            raise SummarisationError("Server timeout. Please try again.")

        else:
            raise SummarisationError(
                f"Summarisation failed with status {response.status_code}."
            )
    except requests.exceptions.Timeout:
        raise SummarisationError("Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        raise SummarisationError(f"Network error: {str(e)}")


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
            timeout=300,
        )
        if response.status_code == 200:
            return response.json()[
                "response"
            ]  # return the response and get the response value(translated text) in dictionary
        elif response.status_code == 504:
            raise TranslationError("Server timeout. Please try again.")
        else:
            raise TranslationError(
                f"Translation failed with status {response.status_code}."
            )
    except requests.exceptions.Timeout:
        raise TranslationError("Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        raise TranslationError(f"Network error: {str(e)}")


# function responsible for the text to speech logic
def text_to_speech(text, language):
    try:

        speaker_id = speaker_ids.get(language)
        if speaker_id is None:
            raise TextToSpeechError("Unsupported language selected.")
        response = requests.post(
            BASE_URL + "/tasks/tts",
            headers=headers,
            json={"text": text, "speaker_id": speaker_id},
            timeout=300,
        )
        if response.status_code == 200:
            return response.json()["output"][
                "audio_url"
            ]  # return the response and tap into the output
            #  dictionary to get the audio path(audio_url) value
        elif response.status_code == 504:
            raise TextToSpeechError("Server timeout. Please try again.")
        else:
            raise TextToSpeechError(
                f"Audio generation failed with status {response.status_code}."
            )
    except requests.exceptions.Timeout:
        raise TextToSpeechError("Request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        raise TextToSpeechError(f"Network error: {str(e)}")
