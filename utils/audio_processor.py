import os
from pydub import AudioSegment
import yt_dlp

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to lightweight 16kHz Mono WAV format for Whisper."""
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)  # 16kHz mono
    audio.export(output_path, format="wav")

    # Clean up raw heavy download file to save disk space
    if os.path.exists(input_path) and input_path != output_path:
        try:
            os.remove(input_path)
        except Exception:
            pass

    return output_path


def download_youtube_audio(url: str) -> str:
    """Fast YouTube audio download using ios/mweb client to bypass speed throttling."""
    output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        # 'ios' and 'mweb' clients bypass YouTube datacenter bandwidth throttling!
        "extractor_args": {"youtube": {"player_client": ["ios", "mweb"]}},
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_audio_path = ydl.prepare_filename(info)

    # Convert small M4A to 16kHz Mono WAV
    return convert_to_wav(raw_audio_path)


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []
    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start : start + chunk_ms]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)

    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
