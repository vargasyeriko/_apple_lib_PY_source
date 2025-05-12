import os

def compute_bitrate(file_path, duration):
    try:
        # Get file size in bytes
        file_size_bytes = os.path.getsize(file_path)
        
        # Calculate bitrate in kbps
        bitrate = (file_size_bytes * 8) / (1000 * duration)
        return bitrate
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return None

# Applying the function to the DataFrame
#df['bitrate'] = df.apply(lambda row: compute_bitrate(row['Path'], row['Duration']), axis=1)
