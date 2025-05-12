
import aubio
import numpy as np
import pandas as pd
from tqdm import tqdm  # Importing tqdm

audio_extensions = ['.m4a', '.mp3', '.MP3', '.Mp3', '.wav', '.WAV', '.flac', '.FLAC', '.aac',
                    '.ogg', '.wma', '.au', '.aif', '.aiff']

def compute_bpm(filename):
    try:
        win_s = 512                 # fft size
        hop_s = win_s // 2          # hop size
        samplerate = 0
        s = aubio.source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        o = aubio.tempo("default", win_s, hop_s, samplerate)
        beats = []
        while True:
            samples, read = s()
            is_beat = o(samples)
            if is_beat:
                this_beat = o.get_last_s()
                beats.append(this_beat)
            if read < hop_s:
                break
        bpms = 60. / np.diff(beats)
        return np.median(bpms)
    except Exception as e:
        print(f"Error processing file {filename}: {str(e)}")
        return None

# Assuming you have a DataFrame called df with a 'Path' column
# df = pd.read_csv('your_dataset.csv')  # Modify this if you've loaded your dataframe differently

# Using tqdm to display a progress bar

#print(df[['Path', 'BPM']])
