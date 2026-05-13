import gradio as gr
import sys
import os
import requests as req
import tempfile

# ensure backend folder is accessible — allows imports from backend folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.sunbird_client import (
    transcribe,
    summarise,
    translate,
    text_to_speech,
    TranscriptionError,
    SummarisationError,
    TranslationError,
    TextToSpeechError,
)


def download_audio(url):
    """
    Downloads audio from a signed URL returned by the TTS API
    and saves it to a temporary local file.
    Returns the local file path so Gradio can play it.
    The signed URL expires after 2 minutes so we download immediately.
    """
    try:
        response = req.get(url, timeout=60)
        response.raise_for_status()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tmp.write(response.content)
            return tmp.name
    except Exception:
        return None


def process(input_type, audio_file, text_input, language):
    """
    Main processing function with streaming.
    Yields intermediate results as each pipeline step completes
    so the user sees progress in real time rather than waiting
    for everything to finish.
    Errors before any yield use gr.Error() for popup notification.
    Errors after a yield clear the outputs first to avoid showing
    Error labels in the output boxes.
    """
    # validate inputs before running anything , no yield has happened yet
    if input_type == "Audio Upload":
        if audio_file is None:
            raise gr.Error("Please upload an audio file to continue.")
    else:
        if not text_input or text_input.strip() == "":
            raise gr.Error("Please enter some text to continue.")

    if not language:
        raise gr.Error("Please select an output language to continue.")

    # step 1 of transcription
    yield "Processing your input...", "", "", None

    if input_type == "Audio Upload":
        try:
            transcript = transcribe(audio_file)
        except TranscriptionError as e:
            # clear outputs then raise so boxes do not show Error label
            yield "", "", "", None
            raise gr.Error(str(e))
    else:
        transcript = text_input

    yield (
        transcript,
        "Generating a summary — this may take up to 2 minutes...",
        "",
        None,
    )

    # step 2 of summarisation
    try:
        summary = summarise(transcript)
    except SummarisationError as e:
        yield transcript, "", "", None
        raise gr.Error(str(e))

    yield transcript, summary, "Translating the summary...", None

    # step 3 of translation
    try:
        translation = translate(summary, language)
    except TranslationError as e:
        yield transcript, summary, "", None
        raise gr.Error(str(e))

    yield transcript, summary, translation, None

    # step 4 of text to speech
    try:
        audio_url = text_to_speech(translation, language)
    except TextToSpeechError as e:
        yield transcript, summary, translation, None
        raise gr.Error(str(e))

    # download audio immediately as signed URL expires in 2 minutes
    local_audio = download_audio(audio_url)

    if local_audio is None:
        yield transcript, summary, translation, None
        raise gr.Error(
            "The audio was generated but could not be loaded. "
            "Please try again."
        )

    yield transcript, summary, translation, local_audio


def toggle_input(input_type):
    """
    Shows or hides the text or audio input
    based on what the user selects.
    """
    if input_type == "Audio Upload":
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=True), gr.update(visible=False)


# supported output languages
LANGUAGES = ["Luganda", "Runyankole", "Ateso", "Lugbara", "Acholi"]

CSS = """
.gradio-container {
    max-width: 960px !important;
    margin: auto;
    font-family: 'DM Sans', sans-serif;
}
.how-it-works {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.info-box {
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 10px;
    padding: 20px 24px;
}
footer {
    display: none !important;
}
"""

THEME = gr.themes.Soft(
    primary_hue="orange",
    secondary_hue="gray",
    font=gr.themes.GoogleFont("DM Sans"),
)

# build the Gradio UI
with gr.Blocks(title="Sunbird AI Language Pipeline") as demo:

    # page header
    gr.Markdown("""
        <div style="text-align: center; padding: 30px 0 20px 0;
        border-bottom: 1px solid #e5e7eb; margin-bottom: 24px;">
            <h1 style="font-size: 26px; font-weight: 700;
            margin-bottom: 8px; color: #111827;">
                Sunbird AI Language Pipeline
            </h1>
            <p style="font-size: 15px; color: #6b7280; margin: 0;">
                Convert text or audio into a summarised, translated,
                and spoken output in a Ugandan local language.
            </p>
        </div>
        """)

    with gr.Row(equal_height=False):

        # left column with inputs and controls
        with gr.Column(scale=3):

            # how it works section
            gr.Markdown("""
                <div class="how-it-works">
                    <p style="font-weight: 600; font-size: 14px;
                    margin-bottom: 12px; color: #111827;">
                        How it works
                    </p>
                    <ol style="margin: 0; padding-left: 18px;
                    color: #374151; font-size: 14px; line-height: 2.2;">
                        <li><strong>Transcription</strong> — Your audio
                        file is converted to text automatically</li>
                        <li><strong>Summarisation</strong> — The text is
                        condensed into a short, clear summary</li>
                        <li><strong>Translation</strong> — The summary is
                        translated into your chosen local language</li>
                        <li><strong>Audio Generation</strong> — The
                        translated summary is read aloud and made
                        available to play</li>
                    </ol>
                </div>
                """)

            # input type toggle
            input_type = gr.Radio(
                choices=["Text Input", "Audio Upload"],
                value="Text Input",
                label="Source Input",
                interactive=True,
            )

            # text input  visible by default
            text_input = gr.Textbox(
                label="Enter Text",
                placeholder="Paste or type your text here...",
                lines=5,
                visible=True,
            )

            # audio input,hidden by default
            audio_input = gr.Audio(
                label=(
                    "Upload Audio File "
                    "(MP3, WAV, OGG, M4A or AAC — maximum 5 minutes)"
                ),
                type="filepath",
                visible=False,
            )

            # output language selector
            language = gr.Dropdown(
                choices=LANGUAGES,
                label="Select Output Language",
                value="Luganda",
                interactive=True,
            )

            # run button
            run_btn = gr.Button(
                "Run Pipeline",
                variant="primary",
                size="lg",
            )

        # right column for info panel
        with gr.Column(scale=2):
            gr.Markdown("""
                <div class="info-box">
                    <p style="font-weight: 600; font-size: 14px;
                    margin-bottom: 12px; color: #111827;">
                        Supported Languages
                    </p>
                    <ul style="margin: 0 0 20px 0; padding-left: 18px;
                    color: #374151; font-size: 14px; line-height: 2.2;">
                        <li>Luganda</li>
                        <li>Runyankole</li>
                        <li>Ateso</li>
                        <li>Lugbara</li>
                        <li>Acholi</li>
                    </ul>
                    <p style="font-weight: 600; font-size: 14px;
                    margin-bottom: 12px; color: #111827;">
                        Audio Requirements
                    </p>
                    <ul style="margin: 0 0 20px 0; padding-left: 18px;
                    color: #374151; font-size: 14px; line-height: 2.2;">
                        <li>Accepted formats: MP3, WAV, OGG, M4A, AAC</li>
                        <li>Maximum duration: 5 minutes</li>
                        <li>Maximum file size: 100MB</li>
                    </ul>
                    <p style="font-size: 13px; color: #6b7280;
                    border-top: 1px solid #e5e7eb;
                    padding-top: 12px; margin: 0;">
                        Processing time varies depending on the length
                        of your input. Summarisation typically takes
                        between 30 seconds and 2 minutes. Results appear
                        as each step completes.
                    </p>
                </div>
                """)

    # results section
    gr.Markdown("---")
    gr.Markdown("""
        <p style="font-weight: 600; font-size: 16px;
        color: #111827; margin-bottom: 4px;">
            Pipeline Results
        </p>
        <p style="font-size: 13px; color: #6b7280; margin-bottom: 8px;">
            Results appear below as each step of the pipeline completes.
        </p>
        """)

    with gr.Row():
        with gr.Column():
            transcript_output = gr.Textbox(
                label="Transcript",
                lines=4,
                interactive=False,
                placeholder="The transcript of your input will appear here.",
            )

    with gr.Row():
        with gr.Column():
            summary_output = gr.Textbox(
                label="Summary",
                lines=4,
                interactive=False,
                placeholder=(
                    "A condensed summary of the transcript "
                    "will appear here."
                ),
            )

    with gr.Row():
        with gr.Column():
            translation_output = gr.Textbox(
                label="Translated Summary",
                lines=4,
                interactive=False,
                placeholder=(
                    "The translated summary in your chosen "
                    "language will appear here."
                ),
            )

    with gr.Row():
        with gr.Column():
            audio_output = gr.Audio(
                label="Generated Audio",
                interactive=False,
            )

    # wire up input toggle
    input_type.change(
        fn=toggle_input,
        inputs=[input_type],
        outputs=[text_input, audio_input],
        show_progress=False,
    )

    # wire up run button with streaming enabled
    run_btn.click(
        fn=process,
        inputs=[input_type, audio_input, text_input, language],
        outputs=[
            transcript_output,
            summary_output,
            translation_output,
            audio_output,
        ],
    )

if __name__ == "__main__":
    demo.launch(
        theme=THEME,
        css=CSS,
    )
