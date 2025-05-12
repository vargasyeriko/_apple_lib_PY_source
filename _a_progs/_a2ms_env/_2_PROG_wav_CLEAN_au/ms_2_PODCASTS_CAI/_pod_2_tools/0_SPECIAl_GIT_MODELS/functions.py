
def convert_to_wav(input_path, output_path):
    # Supported audio formats by pydub
    SUPPORTED_FORMATS = ["mp3", "flv", "ogg", "mp4", "wav", "aif", "wma", "aac", "m4a"]

    # Extract the file extension from input_path
    file_extension = input_path.split('.')[-1].lower()

    # Check if the file format is supported
    if file_extension not in SUPPORTED_FORMATS:
        print(f"Unsupported file format: {file_extension}")
        return

    # Read the audio file
    audio = AudioSegment.from_file(input_path, format=file_extension)

    # Convert to WAV
    audio.export(output_path, format="wav")
    print(f"File has been converted and saved at {output_path}")  # ^^^ path ^^^


# ------------------------------------------------------------------- Function to analyze audio
def analyze_audio(audio_path):
    #from pydub.utils import mediainfo
    audio_info = mediainfo(audio_path)
    length_in_seconds = float(audio_info["duration"])
    channels = int(audio_info["channels"])
    frame_rate = int(audio_info["sample_rate"])

    print(f"Audio duration: {length_in_seconds} seconds")
    print(f"Channels: {channels}")
    print(f"Frame rate: {frame_rate} Hz")
    
    return length_in_seconds, channels, frame_rate


## ------------------------------------------------------------------- Noise Reduction 

def basic_noise_reduction(input_path, output_path):
    # Read the input audio file
    rate, data = wavfile.read(input_path)
    
    # Take a sample of the noise (adjust as needed)
    noise_sample = data[:5000]
    
    # Generate noise profile
    noise_profile = np.mean(np.abs(noise_sample))
    
    # Perform noise reduction: Zero out anything below the profile
    reduced_noise_data = np.where(np.abs(data) < noise_profile, 0, data)
    
    # Save the noise-reduced audio
    wavfile.write(output_path, rate, reduced_noise_data.astype(np.int16))
    print(f"Noise-reduced audio saved at {output_path}")  # ^^^ path ^^^

# ## ------------------------------------------------------------------- ADJUSTABLE Noise Reduction 


def adjustable_noise_reduction(input_path, output_path, threshold_factor=1.0):
    # Read the input audio file
    rate, data = wavfile.read(input_path)
    
    # Take a sample of the noise (adjust the range as needed)
    noise_sample = data[:5000]
    
    # Generate noise profile
    noise_profile = np.mean(np.abs(noise_sample))
    
    # Calculate the adjusted threshold
    adjusted_threshold = noise_profile * threshold_factor
    
    # Perform noise reduction: Zero out anything below the adjusted threshold
    reduced_noise_data = np.where(np.abs(data) < adjusted_threshold, 0, data)
    
    # Save the noise-reduced audio
    wavfile.write(output_path, rate, reduced_noise_data.astype(np.int16))
    print(f"Noise-reduced audio saved at {output_path}")  # ^^^ path ^^^
