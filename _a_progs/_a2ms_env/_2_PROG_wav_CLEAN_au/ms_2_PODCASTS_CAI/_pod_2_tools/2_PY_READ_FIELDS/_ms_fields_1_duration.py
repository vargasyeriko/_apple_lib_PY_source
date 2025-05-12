
import pandas as pd
from pydub.utils import mediainfo
import mutagen
import eyed3
import wave
import audioread
from tinytag import TinyTag
import librosa
import subprocess
from tqdm import tqdm

def get_duration_using_ffprobe(file_path):
    cmd = ["ffprobe", "-i", file_path, "-show_entries", "format=duration", "-v", "quiet", "-of", "csv=p=0"]
    try:
        output = subprocess.check_output(cmd).decode('utf-8').strip()
        return float(output)
    except:
        return None

def get_duration(file_path):
    # Method 1: pydub & ffmpeg
    try:
        info = mediainfo(file_path)
        duration = float(info['duration'])
        return duration
    except:
        pass

    # Method 2: mutagen
    try:
        audio = mutagen.File(file_path)
        return audio.info.length
    except:
        pass

    # Method 3: eyed3
    try:
        audio = eyed3.load(file_path)
        return audio.info.time_secs
    except:
        pass

    # Method 4: wave (for WAV files)
    try:
        with wave.open(file_path, 'rb') as f:
            frames = f.getnframes()
            rate = f.getframerate()
            duration = frames / float(rate)
            return duration
    except:
        pass

    # Method 5: audioread
    try:
        with audioread.audio_open(file_path) as f:
            return f.duration
    except:
        pass

    # Method 6: tinytag
    try:
        tag = TinyTag.get(file_path)
        return tag.duration
    except:
        pass

    # Method 7: librosa
    try:
        y, sr = librosa.load(file_path, sr=None, mono=True)
        return len(y) / sr
    except:
        pass

    # Method 8: ffprobe
    duration = get_duration_using_ffprobe(file_path)
    if duration is not None:
        return duration

    # If all methods fail, annotate
    return f"Failed to process: {file_path}"

