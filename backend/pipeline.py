from backend.sunbird_client import transcribe, summarise, translate, text_to_speech


def run_pipeline(input_type, audio_file, text_input, language):
    if input_type == "audio":
        transcript = transcribe(audio_file)
    else:
        transcript = text_input
    summary = summarise(transcript)
    translation = translate(summary, language)
    audio_url = text_to_speech(translation, language)
    return {
        "transcript": transcript,
        "summary": summary,
        "translation": translation,
        "audio_url": audio_url,
    }
