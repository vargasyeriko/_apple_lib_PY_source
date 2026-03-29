
from tinytag import TinyTag
from mutagen import File
from pydub.utils import mediainfo
from tqdm import tqdm
import pandas as pd

def extract_metadata_optimized(file_path):
    """Extracts metadata from an audio file using multiple methods to ensure maximum coverage."""
    results = {}

    # Using Mutagen for comprehensive metadata extraction.
    try:
        audio = File(file_path, easy=True)
        results = {k.replace(":", "_"): v[0] for k, v in audio.items()}
    except Exception:
        pass

    # Using TinyTag as a fallback.
    try:
        tag = TinyTag.get(file_path)
        results['idt_title'] = results.get('idt_title', tag.title)
        results['idt_artist'] = results.get('idt_artist', tag.artist)
        results['idt_album'] = results.get('idt_album', tag.album)
        results['idt_year'] = results.get('idt_year', tag.year)
        results['idt_track'] = results.get('idt_track', tag.track)
        results['idt_genre'] = results.get('idt_genre', tag.genre)
        results['idt_comment'] = results.get('idt_comment', tag.comment)
        results['idt_audio_offset'] = results.get('idt_audio_offset', tag.audio_offset)
    except Exception:
        pass

    # Using pydub's mediainfo as a further fallback.
    try:
        tag = mediainfo(file_path)
        results['idt_title'] = results.get('idt_title', tag.get('title'))
        results['idt_artist'] = results.get('idt_artist', tag.get('artist'))
        results['idt_album'] = results.get('idt_album', tag.get('album'))
        results['idt_year'] = results.get('idt_year', tag.get('date'))  # Mediainfo sometimes uses 'date' for year
        results['idt_track'] = results.get('idt_track', tag.get('track'))
        results['idt_genre'] = results.get('idt_genre', tag.get('genre'))
        results['idt_comment'] = results.get('idt_comment', tag.get('comment'))
    except Exception:
        pass

    return results

def process_metadata_optimized(dataframe, file_column='FilePath'):
    """Processes all rows in a DataFrame to extract metadata."""
    errors = []
    for index, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0], desc="Processing Files"):
        try:
            metadata = extract_metadata_optimized(row[file_column])
            for key, value in metadata.items():
                dataframe.at[index, key] = value
        except Exception as e:
            errors.append((index, e))

    # Report errors
    for idx, error in errors:
        print(f"Error at index {idx}: {error}")

    return dataframe


