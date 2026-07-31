import os
import re
import requests
import whisper
from pydub import AudioSegment
from youtube_transcript_api import YouTubeTranscriptApi

SARVAM_PIECE_SECONDS = 25
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "tiny")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

_model = None


def extract_youtube_id(url: str) -> str:
    if not url or not isinstance(url, str):
        return None
    pattern = r"(?:v=|\/|vi=)([^" "&?\/\s]{11})"
    match = re.search(pattern, url)
    return match.group(1) if match else None


def try_get_youtube_transcript(url: str) -> str:
    video_id = extract_youtube_id(url)
    if not video_id:
        return None

    try:
        transcript_list = YouTubeTranscriptApi.get_transcript(
            video_id, languages=["en", "hi", "en-IN"]
        )
        return " ".join([item["text"] for item in transcript_list])
    except Exception:
        return None


def load_model():
    global _model
    if _model is None:
        _model = whisper.load_model(WHISPER_MODEL)
    return _model


def transcribe_chunk_whisper(chunk_path: str) -> str:
    model = load_model()
    result = model.transcribe(chunk_path, task="transcribe")
    return result["text"]


def _send_to_sarvam(piece_path: str) -> str:
    headers = {"api-subscription-key": SARVAM_API_KEY}
    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:
        response.raise_for_status()
    return response.json().get("transcript", "")


def transcribe_chunk_sarvam(chunk_path: str) -> str:
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set in environment / .env")

    audio = AudioSegment.from_wav(chunk_path)
    piece_ms = SARVAM_PIECE_SECONDS * 1000
    full_text = ""

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start : start + piece_ms]
        piece_path = f"{chunk_path}_sv_{i}.wav"
        piece.export(piece_path, format="wav")
        try:
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()


def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)


def transcribe_all(
    chunks: list, language: str = "english", source: str = None
) -> str:
    if source and (source.startswith("http://") or source.startswith("https://")):
        fast_transcript = try_get_youtube_transcript(source)
        if fast_transcript:
            return fast_transcript

    full_transcript = ""
    for chunk in chunks:
        text = transcribe_chunk(chunk, language=language)
        full_transcript += text + " "

    return full_transcript.strip()
