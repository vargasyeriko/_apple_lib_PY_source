

import shutil, os
import pandas as pd
from pathlib import Path

taken_acronym = input('what is 4 CHARACTER df key word acronym \n\n')
acronym = 't'
folder_list = folder_list 
counter = 0
dfs = []

for path in folder_list:
    try:
        print(f"\n🔁 Processing: {path}")
        my_aiff = path
        direc_jpg = "images/"
        direc_tables = "tables/"
        silence_id = counter + 1
        print(f"📎 Assigned Silence ID = {silence_id}")
        exec(open("run.py", encoding="utf-8").read())

        pkl_name = f"df_{counter:03d}_.pkl"
        df.to_pickle(pkl_name)
        dfs.append(df)
        print(f"✅ Saved: {pkl_name}")
        [shutil.rmtree(f, ignore_errors=True) or os.makedirs(f, exist_ok=True) for f in [direc_jpg, direc_tables]]
        print('images and tables folders erased')
        counter += 1

    except Exception as e:
        print(f"❌ Error in {path}: {e}")
        continue

# ───── CONCAT VOCALS TABLES ─────
final_df = pd.concat(dfs, ignore_index=True)
final_path = f"df_{taken_acronym}{acronym}_final.pkl"
final_df.to_pickle(final_path)
print(f"\n📦 Final vocals DF saved as: {final_path}")

# ───── DELETE TEMP PICKLES ─────
for i in range(counter):
    f = Path(f"df_{i:03d}_.pkl")
    if f.exists():
        f.unlink()
print("🗑️ Temp pickle files deleted.")

# ───── CLEAN MEMORY ─────
del df
dfs = []