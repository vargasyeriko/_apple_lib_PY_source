###############################################################

from scipy.io import wavfile
import numpy as np

def wav_norm_mod_1(file_path, output_path):
    # Read WAV file
    sample_rate, data = wavfile.read(file_path)
    
    # Classify the variation
    std_dev = np.std(data)
    if std_dev < 2000:
        variation = "low_variation"
        scaling_factor = 0.5
    elif std_dev < 4000:
        variation = "medium_variation"
        scaling_factor = 0.7
    else:
        variation = "high_variation"
        scaling_factor = 1.0

    # Normalize the audio data
    normalized_data = np.int16(data / np.max(np.abs(data)) * 32767 * scaling_factor)

    # Save the normalized audio
    wavfile.write(output_path, sample_rate, normalized_data)

    # Return summary information
    return sample_rate, variation, scaling_factor

###############################################################
import soundfile as sf
import numpy as np
from scipy.signal import butter, lfilter

def wav_norm_mod_2(file_path, outfile_path):
    def rms_normalization(audio_signal, gain=0.9):
        rms_value = np.sqrt(np.mean(np.square(audio_signal)))
        normalized_audio = gain * (audio_signal / rms_value)
        return normalized_audio
    
    def peak_normalization(audio_signal):
        peak_value = np.max(np.abs(audio_signal))
        return audio_signal / peak_value
    
    def z_score_normalization(audio_signal):
        mean = np.mean(audio_signal)
        std = np.std(audio_signal)
        return (audio_signal - mean) / std
    
    def compress_dynamic_range(audio_signal, threshold=0.015, ratio=.002):
        compressed_audio = np.where(np.abs(audio_signal) > threshold,
                                    threshold + ((np.abs(audio_signal) - threshold) / ratio),
                                    audio_signal)
        return np.sign(audio_signal) * compressed_audio
    
    def butter_lowpass_filter(audio_signal, cutoff_freq, sample_rate):
        b, a = butter(6, cutoff_freq / (0.5 * sample_rate), btype='low')
        return lfilter(b, a, audio_signal)
    
    #def wav_norm_pick_mod_2(file_path, outfile_path):
    # ^^^ path ^^^
    audio_data, sample_rate = sf.read(file_path)
    
    print("Choose the type of normalization:")
    print("1: Z-Score Normalization with Pre-Filtering         _for_  *     LOW Level of Background Noise")
    print("2: Peak Normalization with Dynamic Range Compression_for_  ***   MID Level of Background Noise")
    print("3: RMS Normalization with Gain Control              _for_  ***** HIGH Level of Background Noise ")
    

    
    choice = input("Enter the number corresponding to your choice: ")

    if choice == '1':
        filtered_audio = butter_lowpass_filter(audio_data, cutoff_freq=3000, sample_rate=sample_rate)
        normalized_audio = z_score_normalization(filtered_audio)
        norm_type = 'z_score_pre_filtering'
        
    elif choice == '2':
        compressed_audio = compress_dynamic_range(audio_data)
        normalized_audio = peak_normalization(compressed_audio)
        norm_type = 'peak_norm_dynamic'

    elif choice == '3':
        normalized_audio = rms_normalization(audio_data, gain=0.7)
        norm_type = 'rms_norm_gain_control'

    else:
        print("Invalid choice. Exiting.")
        exit()

    # ^^^ path ^^^
    sf.write(outfile_path, normalized_audio, sample_rate)
    print(f'\n\n NORM TYPE {norm_type}' )
    
# if __name__ == '__main__':
#      main()
########################################################
