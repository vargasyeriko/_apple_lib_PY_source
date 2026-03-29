


from mutagen.m4a import M4A
from tinytag import TinyTag
from pydub.utils import mediainfo
from tqdm import tqdm
import pandas as pd

def extract_metadata_optimized_m4a(file_path):
    """Extracts metadata from an M4A audio file using multiple methods to ensure maximum coverage."""
    results = {}

    # Using Mutagen for M4A files
    try:
        audio = M4A(file_path)
        for k, v in audio.items():
            key_name = "idt_" + k.replace("©", "").lower()
            results[key_name] = v[0]
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

def process_metadata_optimized_m4a(dataframe, file_column='FilePath'):
    """Processes all rows in a DataFrame to extract metadata."""
    errors = []
    for index, row in tqdm(dataframe.iterrows(), total=dataframe.shape[0], desc="Processing M4A Files"):
        try:
            metadata = extract_metadata_optimized_m4a(row[file_column])
            for key, value in metadata.items():
                dataframe.loc[index, key] = value
        except Exception as e:
            errors.append((index, e))

    # Report errors
    for idx, error in errors:
        print(f"Error at index {idx}: {error}")

    return dataframe
