
# =========================================================
# -----######-----######  CORE FUNCTION  -----######-----###
# =========================================================

import os
import pandas as pd
from tqdm import tqdm

def _ren_1803_i5_GET_df_samples(samples_path):

    data = []
    counter_dict = {}

    for root, dirs, files in os.walk(samples_path):

        # 🔒 skip root _SAMPLES
        if root == samples_path:
            continue

        folder_name = os.path.basename(root)

        if folder_name not in counter_dict:
            counter_dict[folder_name] = 1

        for file in tqdm(files, desc=f"Processing {folder_name}"):

            # skip hidden/system
            if file.startswith('.') or file.startswith('._'):
                continue

            # 🔒 SKIP already renamed files
            if file.startswith(f"{folder_name}_"):
                continue

            old_path = os.path.join(root, file)

            if not os.path.isfile(old_path):
                continue

            name, ext = os.path.splitext(file)

            i = counter_dict[folder_name]

            new_name = f"{folder_name}_{i}_{name}{ext}"
            new_path = os.path.join(root, new_name)

            os.rename(old_path, new_path)

            file_size = os.path.getsize(new_path)

            data.append({
                "folder": folder_name,
                "file_name_old": file,
                "file_name_new": new_name,
                "name_old": name,
                "name_new": f"{folder_name}_{i}_{name}",
                "ext": ext.lower(),
                "Path_old": old_path,
                "Path": new_path,
                "file_size_bytes": file_size
            })

            counter_dict[folder_name] += 1

    df = pd.DataFrame(data)

    print(f"✅ Total files processed: {len(df)}")

    return df
