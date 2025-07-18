# v_folders = [
#     "/Volumes/MUSIC_PROD/STEMS_24_years/v__RNRNexports/30_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/v__RNRNexports/40_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/v__RNRNexports/50_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/v__RNRNexports/60_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/v__RNRNexports/70_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/v__RNRNexports/80_percent_silence",
# ]
# b_folders = [
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/10_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/20_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/30_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/40_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/50_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/60_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/70_percent_silence",
#     "/Volumes/MUSIC_PROD/STEMS_24_years/b__RNRNexports/80_percent_silence",
# ]

d_folders = [
    "/Volumes/MUSIC_PROD/STEMS_24_years/d__RNRNexports/60_percent_silence",
    "/Volumes/MUSIC_PROD/STEMS_24_years/d__RNRNexports/70_percent_silence",
    "/Volumes/MUSIC_PROD/STEMS_24_years/d__RNRNexports/80_percent_silence",
]

# v_folders = [
#     "/Users/yerik/Desktop/STEMS/vocals/10_percent_silence",
#     "/Users/yerik/Desktop/STEMS/vocals/20_percent_silence",
#     "/Users/yerik/Desktop/STEMS/vocals/30_percent_silence"
# ]


# b_folders = [
#     "/Users/yerik/Desktop/STEMS/bass/10_percent_silence",
#     "/Users/yerik/Desktop/STEMS/bass/20_percent_silence",
#     "/Users/yerik/Desktop/STEMS/bass/30_percent_silence"
# ]

# d_folders = [
#     "/Users/yerik/Desktop/STEMS/drums/10_percent_silence",
#     "/Users/yerik/Desktop/STEMS/drums/20_percent_silence",
#     "/Users/yerik/Desktop/STEMS/drums/30_percent_silence"
# ]


global_counter = 5

# import shutil, os
# import pandas as pd
# from pathlib import Path
# #import pydub

# # ───── VOCALS ─────
# genre_rn = 'vocals'
# rel_yr_rn = '2025'
# acronym = 'v'
# rn_custom_genre = "STEMS-vocals"
# folder_list = v_folders
# counter = global_counter
# dfs = []

# for path in folder_list:
#     try:
#         print(f"\n🔁 Processing: {path}")
#         my_aiff = path
#         direc_jpg = "images/"
#         direc_tables = "tables/"
#         silence_id = counter + 1
#         print(f"📎 Assigned Silence ID = {silence_id}")
#         exec(open("run.py", encoding="utf-8").read())

#         pkl_name = f"df_{counter:03d}_.pkl"
#         df.to_pickle(pkl_name)
#         dfs.append(df)
#         print(f"✅ Saved: {pkl_name}")
#         [shutil.rmtree(f, ignore_errors=True) or os.makedirs(f, exist_ok=True) for f in [direc_jpg, direc_tables]]
#         print('images and tables folders erased')
#         counter += 1

#     except Exception as e:
#         print(f"❌ Error in {path}: {e}")
#         continue

# # ───── CONCAT VOCALS TABLES ─────
# final_df = pd.concat(dfs, ignore_index=True)
# final_path = f"df_{acronym}_final.pkl"
# final_df.to_pickle(final_path)
# print(f"\n📦 Final vocals DF saved as: {final_path}")

# # ───── DELETE TEMP PICKLES ─────
# # for i in range(counter):
# #     f = Path(f"df_{i:03d}_.pkl")
# #     if f.exists():
# #         f.unlink()
# # print("🗑️ Temp pickle files deleted.")
# # ───── MOVE TEMP PICKLES TO _0_temp_tables ─────
# pkl_output_folder = Path("_0_temp_tables")
# pkl_output_folder.mkdir(exist_ok=True)

# for i in range(counter):
#     src = Path(f"df_{i:03d}_.pkl")
#     dst = pkl_output_folder / src.name
#     if src.exists():
#         src.rename(dst)

# print(f"📂 Chunk pickles moved to: {pkl_output_folder.resolve()}")

# # ───── CLEAN MEMORY ─────
# del df
# dfs = []

# ───── BASS ─────

# genre_rn = 'bass'
# rel_yr_rn = '2025'
# acronym = 'b'
# rn_custom_genre="STEMS-bass"
# folder_list = b_folders 
# counter = global_counter

# dfs = []

# for path in folder_list:
#     try:
#         print(f"\n🔁 Processing: {path}")
#         my_aiff = path
#         direc_jpg = "images/"
#         direc_tables = "tables/"
        
#         silence_id = counter + 1
#         print(f"📎 Assigned Silence ID = {silence_id}")

#         exec(open("run.py", encoding="utf-8").read())

#         pkl_name = f"df_{counter:03d}_.pkl"
#         df.to_pickle(pkl_name)
#         dfs.append(df)
#         print(f"✅ Saved: {pkl_name}")
#         [shutil.rmtree(f, ignore_errors=True) or os.makedirs(f, exist_ok=True) for f in [direc_jpg, direc_tables]]
#         print('images and tables folders erased')
#         counter += 1

#     except Exception as e:
#         print(f"❌ Error in {path}: {e}")
#         continue

# # ───── CONCAT VOCALS TABLES ─────
# final_df = pd.concat(dfs, ignore_index=True)
# final_path = f"df_{acronym}_final.pkl"
# final_df.to_pickle(final_path)
# print(f"\n📦 Final vocals DF saved as: {final_path}")

# # ───── DELETE TEMP PICKLES ─────
# # for i in range(counter):
# #     f = Path(f"df_{i:03d}_.pkl")
# #     if f.exists():
# #         f.unlink()
# # print("🗑️ Temp pickle files deleted.")
# # ───── MOVE TEMP PICKLES TO _0_temp_tables ─────
# pkl_output_folder = Path("_0_temp_tables")
# pkl_output_folder.mkdir(exist_ok=True)

# for i in range(counter):
#     src = Path(f"df_{i:03d}_.pkl")
#     dst = pkl_output_folder / src.name
#     if src.exists():
#         src.rename(dst)

# print(f"📂 Chunk pickles moved to: {pkl_output_folder.resolve()}")

# # ───── CLEAN MEMORY ─────
# del df
# dfs = []

# ───── DRUMS ─────

genre_rn = 'drums'
rel_yr_rn = '2025'
acronym = 'd'
rn_custom_genre="STEMS-drums"
folder_list = d_folders 
counter = global_counter

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
final_path = f"df_{acronym}_final.pkl"
final_df.to_pickle(final_path)
print(f"\n📦 Final vocals DF saved as: {final_path}")

# ───── DELETE TEMP PICKLES ─────
# ───── MOVE TEMP PICKLES TO _0_temp_tables ─────
pkl_output_folder = Path("_0_temp_tables")
pkl_output_folder.mkdir(exist_ok=True)

for i in range(counter):
    src = Path(f"df_d{i:03d}_.pkl")
    dst = pkl_output_folder / src.name
    if src.exists():
        src.rename(dst)

print(f"📂 Chunk pickles moved to: {pkl_output_folder.resolve()}")

# for i in range(counter):
#     f = Path(f"df_{i:03d}_.pkl")
#     if f.exists():
#         f.unlink()
# print("🗑️ Temp pickle files deleted.")

# ───── CLEAN MEMORY ─────
del df
dfs = []