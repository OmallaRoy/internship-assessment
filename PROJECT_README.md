# Sunbird AI Language Pipeline

## Project Description

This application takes either a text input or an uploaded audio file and runs it through a four-step pipeline powered entirely by the Sunbird AI API. The pipeline transcribes audio to text, generates a concise summary of the content, translates the summary into a chosen Ugandan local language, and produces an audio clip of the translated summary that can be played directly in the browser. The goal is to make information accessible across language barriers, particularly for Ugandan languages that are underserved by mainstream AI tools.

---

## Architecture Overview

The pipeline follows this sequence for every request:

```
User Input (text or audio)
        |
        v
[1] Transcription
    Sunbird STT API: POST /tasks/stt
    Converts uploaded audio file to text
        |
        v
[2] Summarisation
    Sunbird Sunflower LLM: POST /tasks/sunflower_simple
    Condenses the text into a short, clear summary
        |
        v
[3] Translation
    Sunbird Sunflower LLM: POST /tasks/sunflower_simple
    Translates the summary into the chosen Ugandan language
        |
        v
[4] Text-to-Speech
    Sunbird TTS API: POST /tasks/tts
    Generates an audio clip of the translated summary
        |
        v
Output displayed to user
(transcript, summary, translated summary, audio player)
```

**File structure:**

```
internship-assessment/
├── app.py                      Gradio frontend and pipeline orchestration
├── backend/
│   ├── __init__.py             Makes backend a Python package
│   ├── sunbird_client.py       Wrapper functions for all Sunbird API calls
│   └── pipeline.py             Pipeline orchestration helper
├── exercises/
│   └── basics.py               Part 1 programming exercises
├── tests/
│   └── test_basics.py          Part 1 test files
├── screenshots/                Screenshots used in this documentation
├── requirements.txt            Python dependencies
├── .env                        Your local environment variables (never committed)
├── .env.example                Template showing required environment variables
├── .gitignore                  Files and folders excluded from version control
├── constants.py                Constants used in Part 1 exercises
├── README.md                   Original assessment readme
└── PROJECT_README.md           This file
```

---

## Local Setup

Follow these steps exactly to run the app on your machine.

**1. Clone the repository**

```bash
git clone https://github.com/OmallaRoy/internship-assessment.git
cd internship-assessment
```

**2. Create and activate a virtual environment**

```bash
python -m venv venv
```

On Windows:
```bash
venv\Scripts\activate.bat
```

On Mac or Linux:
```bash
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Set up environment variables**

Copy the example file and add your Sunbird API token:

```bash
cp .env.example .env
```

Open `.env` and replace the placeholder with your actual token:

```
SUNBIRD_API_TOKEN=your_actual_token_here
```

You can get a token by signing up at https://api.sunbird.ai/

**5. Run the app**

```bash
python app.py
```

Then open http://127.0.0.1:7860 in your browser.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `SUNBIRD_API_TOKEN` | Yes | Your Sunbird AI API bearer token. Used to authenticate all API requests. Get one from https://api.sunbird.ai/ |

---

## Usage

**Text input:**

1. Select "Text Input" from the Source Input toggle
2. Paste or type your text in the text box
3. Select your preferred output language from the dropdown
4. Click "Run Pipeline"
5. Watch as each result appears including transcript, summary, translated summary, and audio

**Audio upload:**

1. Select "Audio Upload" from the Source Input toggle
2. Upload an audio file (MP3, WAV, OGG, M4A or AAC, maximum 5 minutes)
3. Select your preferred output language
4. Click "Run Pipeline"
5. Results appear step by step as the pipeline processes your audio

Results stream in as each step completes so you do not have to wait for everything to finish before seeing progress.

---

## Screenshots

**1. Default view with text input selected**

![Text input view](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/01_text_input.jpg)

**2. Audio upload view after switching input type**

![Audio upload view](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/02_audio_upload.jpg)

**3. Pipeline running with results appearing in real time**

![Pipeline running](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/03_pipeline_running.jpg)

**4. Complete result showing all four outputs**

![Full result](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/04_transcript_result.jpg)
![Full result](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/05_other_result.jpg)

**5. Validation error when no input is provided**

![Error handling](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/06_error_handling.jpg)

**6. Audio duration error when file exceeds 5 minutes**

![Audio too long error](https://raw.githubusercontent.com/OmallaRoy/internship-assessment/main/screenshots/07_audio_too_long.jpg)

---

## Deployed Link

[https://huggingface.co/spaces/OmallaRoy/uganda-speech-text-pipeline](https://huggingface.co/spaces/OmallaRoy/uganda-speech-text-pipeline)
> **Note:** The application is hosted on the Hugging Face Spaces free tier, which automatically pauses the Space after a period of inactivity. A third-party monitoring service has been configured to ping the Space periodically to minimise cold starts, but an occasional short delay on first load may still occur.
---

## Known Limitations

- **Processing time** : Summarisation uses the Sunflower LLM which can take between 30 seconds and 5 minutes depending on text length and server load on the free tier. This is a server-side limitation and not something the application can control.

- **Free tier rate limits** : The Sunbird free tier allows up to 50 requests per minute. Running multiple requests in quick succession may result in temporary rate limiting.

- **Audio URL expiry** : The text to speech API returns a signed URL that expires after 2 minutes. The app downloads the audio immediately to avoid playback issues, but very slow connections may occasionally miss the window.

- **M4A audio format** : While M4A files are accepted by the app, the Sunbird STT API occasionally returns a server error when processing M4A files. If this happens, converting the file to MP3 or WAV before uploading will resolve the issue.

- **Supported audio formats** : Only MP3, WAV, OGG, M4A and AAC are accepted. Other formats will be rejected with a clear error message before the file is sent to the API.

- **Supported languages** : Translation and TTS are limited to the five Ugandan languages supported by the Sunbird API: Luganda, Runyankole, Ateso, Lugbara, and Acholi.

- **Audio duration** : Files longer than 5 minutes are rejected before being sent to the API. The Sunbird speech to text API itself trims audio at 10 minutes, but this app enforces a stricter 5-minute limit as required by the assessment.
