
import pandas as pd
import librosa
from tqdm import tqdm

def direc_wav_read_pa(df, path_col_name='Path', amplitude_col='peak_amp'):
    """
    Adds a column to the DataFrame with the peak amplitudes of the audio files.

    Parameters:
    df (DataFrame): DataFrame with a column containing file paths to audio files.
    path_col_name (str): Name of the column in df that contains the file paths.
    amplitude_col (str): Name of the new column to be added with peak amplitudes.

    Returns:
    DataFrame: The original DataFrame with a new column containing peak amplitudes.
    """

    def get_peak_amplitude(file_path):
        try:
            audio_data, _ = librosa.load(file_path, sr=None)
            return max(abs(audio_data))
        except Exception as e:
            return f"Error: {e}"

    if path_col_name in df.columns:
        tqdm.pandas(desc="Processing audio files for peak amplitude")
        df[amplitude_col] = df[path_col_name].progress_apply(get_peak_amplitude)
    else:
        raise ValueError(f"'{path_col_name}' column not found in DataFrame")

    return df

# Example usage:
# data = {'Path': ['path/to/audio1.wav', 'path/to/audio2.wav']}
# df = pd.DataFrame(data)
# df_with_amplitude = add_peak_amplitude_to_dataframe(df)
# print(df_with_amplitude)
