import pandas as pd
import wave

def direc_wav_read_sr(df, path_col_name='Path', new_col_name='sr'):
    """
    Adds a column to the DataFrame with the sample rates of the audio files.

    Parameters:
    df (DataFrame): DataFrame with a column containing file paths to audio files.
    path_col_name (str): Name of the column in df that contains the file paths.
    new_col_name (str): Name of the new column to be added with sample rates.

    Returns:
    DataFrame: The original DataFrame with a new column containing sample rates.
    """

    def get_sample_rate(file_path):
        """
        Reads the sample rate of a given audio file.

        Parameters:
        file_path (str): Path to the audio file.

        Returns:
        int or str: The sample rate of the audio file or error message.
        """
        try:
            with wave.open(file_path, 'r') as audio_file:
                return audio_file.getframerate()
        except Exception as e:
            return f"Error: {e}"

    if path_col_name in df.columns:
        df[new_col_name] = df[path_col_name].apply(get_sample_rate)
    else:
        raise ValueError(f"'{path_col_name}' column not found in DataFrame")

    return df

# Example usage:
# data = {'Path': ['path/to/audio1.wav', 'path/to/audio2.wav']}
# df = pd.DataFrame(data)
# df_with_sample_rates = add_sample_rates_to_dataframe(df)
# print(df_with_sample_rates)
