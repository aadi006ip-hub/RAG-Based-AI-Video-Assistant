import os
from pydub import AudioSegment
import yt_dlp

DOWNLOAD_DIR = "downloades"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    audio = AudioSegment.from_file(input_path)
    audio = audio.set_channels(1).set_frame_rate(16000)
    audio.export(output_path, format="wav")

    if os.path.exists(input_path) and input_path != output_path:
        try:
            os.remove(input_path)
        except Exception:
            pass

    return output_path


def download_youtube_audio(url: str) -> str:
    output_template = os.path.join(DOWNLOAD_DIR, "%(id)s.%(ext)s")

    ydl_opts = {
        "format": "m4a/bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "nocheckcertificate": True,
        "geo_bypass": True,
        # Real Browser Headers to bypass YouTube bot block
        "http_headers": {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                " (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": (
                "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
            ),
            "Accept-Language": "en-us,en;q=0.5",
        },
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "mweb", "android"],
                "player_skip": ["webpage", "configs"],
            }
        },
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            raw_audio_path = ydl.prepare_filename(info)

        return convert_to_wav(raw_audio_path)
    except Exception as e:
        raise RuntimeError(
            f"YouTube Bot Block: {str(e)}\n\n💡 Tip: YouTube link ki jagah"
            " direct Audio/Video file upload karein!"
        )


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
        wav_path = download_youtube_audio(source)
    else:
        wav_path = convert_to_wav(source)

    chunks = chunk_audio(wav_path)
    return chunks
