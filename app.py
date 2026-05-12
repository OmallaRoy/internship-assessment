import gradio as gr
import sys
import os

# ensure backend folder is accessible ,allows imports from backend folder
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.sunbird_client import (
    transcribe,
    summarise,
    translate,
    text_to_speech,
)


def process(input_type, audio_file, text_input, language):
    """
    Main processing function with streaming — yields results as each
    pipeline step completes so the user sees progress in real time.
    """
    # validate inputs
    if input_type == "Audio Upload":
        if audio_file is None:
            yield "Please upload an audio file.", "", "", None
            return
    else:
        if not text_input or text_input.strip() == "":
            yield "Please enter some text.", "", "", None
            return

    if not language:
        yield "Please select a language.", "", "", None
        return

    # step 1 of transcription
    yield "Transcribing...", "", "", None

    if input_type == "Audio Upload":
        transcript = transcribe(audio_file)
    else:
        transcript = text_input

    if transcript.startswith("Error") or transcript.startswith("Unsupported"):
        yield transcript, "", "", None
        return

    yield transcript, "Summarising — this may take up to 2 minutes...", "", None

    # step 2 of summarisation
    summary = summarise(transcript)

    if summary.startswith("Error") or summary.startswith("Network"):
        yield transcript, summary, "", None
        return

    yield transcript, summary, "Translating...", None

    # step 3 of translation
    translation = translate(summary, language)

    if translation.startswith("Error") or translation.startswith("Network"):
        yield transcript, summary, translation, None
        return

    yield transcript, summary, translation, None

    # step 4 of text to speech
    audio_url = text_to_speech(translation, language)

    if isinstance(audio_url, str) and audio_url.startswith("Error"):
        yield transcript, summary, translation, None
        return

    yield transcript, summary, translation, audio_url


def toggle_input(input_type):
    """
    Shows or hides text or audio input based on user selection.
    """
    if input_type == "Audio Upload":
        return gr.update(visible=False), gr.update(visible=True)
    else:
        return gr.update(visible=True), gr.update(visible=False)


# supported languages
LANGUAGES = ["Luganda", "Runyankole", "Ateso", "Lugbara", "Acholi"]

# build the UI
with gr.Blocks(
    title="Sunbird AI Language Pipeline",
    theme=gr.themes.Soft(
        primary_hue="orange",
        secondary_hue="gray",
        font=gr.themes.GoogleFont("DM Sans"),
    ),
    css="""
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
    """,
) as demo:

    # header
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

        # left column — input and controls
        with gr.Column(scale=3):

            # how it works
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

            # input type selection
            input_type = gr.Radio(
                choices=["Text Input", "Audio Upload"],
                value="Text Input",
                label="Source Input",
                interactive=True,
            )

            # text input — visible by default
            text_input = gr.Textbox(
                label="Enter Text",
                placeholder="Paste or type your text here...",
                lines=5,
                visible=True,
            )

            # audio input — hidden by default
            audio_input = gr.Audio(
                label=(
                    "Upload Audio File "
                    "(MP3, WAV, OGG, M4A or AAC — maximum 5 minutes)"
                ),
                type="filepath",
                visible=False,
            )

            # language selection
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

        # right column — info panel
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

    # divider and results header
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

    # output components
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

    # wire up toggle — show/hide input based on selection
    input_type.change(
        fn=toggle_input,
        inputs=[input_type],
        outputs=[text_input, audio_input],
        show_progress=False,
    )

    # wire up run button with streaming
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
    demo.launch()
