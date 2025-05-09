folder_list = ['/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_09_AN_ArtPArk',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_04_NEW_LODGE',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_06_ttt_SPKRBOX',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_12_Tangent_Debout',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_11_AN_SpotLite',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_02_AN_LA_VENTANA',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_10_Detroit_Hou_Tech',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_04_Foundation_Hotel',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_08_SL_ACAPELLAS',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_08_Barefoot',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_03_Love_Lang',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2023_this/_23_05_AN_bigPINK',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/___YODJ_N0Supervisi0n',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_06_Metroplex_2_and_RNDMgood',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_04_BBssBBssBBs_BandCamp',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_11_11_albm_LordECHO_JAZZ',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/___DJ_friends_Nun',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_07_Puma_BurningMan_indian',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_11_Dinner_Materia_Puma_Jazzy',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_11_11_albm_MimSuleiman_TRIBAL',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_12_fixed_and_added',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_04_NorthL_BadBunny_LatinFast',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_05_MVMNT_block_is_HOT',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_12_Dinner_HipHop_Indian_Puma',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_11_11_N0_Supervisi0n_SPKRbox',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_09_Ghettotech_HiTECH_stu',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_08_Barefoot_and_FREE',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_06_Metroplex_1_and_RNDMgood',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_06_Detroit_Brazil_Funky',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_12_NYE_25',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_09_Eagle_SPKR_Techno',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2024_this/__24_08_Xime_13_Memorial',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_05_Carla_ARABIC_BDAY_LENA',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_BP_Rapharazzi_BDAY',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_03_CAPSULE_House_Latin_1',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_BCAL_SalsaEstrellasPa',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_BCAL_TerapiaLatina',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_05_bc_LowKEY_thirdST_puma_LATIN_4',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_02_DETROIT_PUMA_SPKR',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_02_CDMX_SecretoRoom',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_salsa_VENEZUELA',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_Zbachata_REMIXES',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_BP_ximMAYBDAY_HOUSY_PARTY_LATIN_3',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_04_BP_LATIN_HOUSE_2',
 '/Users/yerik/Music/_1_NEW_SOURCE/_2025_this/__25_05_Movement_DARK_DANCY_LATIN_5']
# counter = 0

# for path in folder_list:
#     try:
#         print(f"\n🔁 Processing: {path}")
#         my_aiff = path
#         direc_jpg = "images/"
#         direc_tables = "tables/"

#         # Execute external script
#         exec(open("run.py", encoding="utf-8").read())

#         # Save first row of df using custom file name format
#         pkl_name = f"df_{counter:03d}_.pkl"
#         df.to_pickle(pkl_name)
#         print(f"✅ Saved: {pkl_name}")
#         [shutil.rmtree(f, ignore_errors=True) or os.makedirs(f, exist_ok=True) for f in ['images/', 'tables/']]
#         print('images and tables folders erased')
#         counter += 1

#     except Exception as e:
#         print(f"❌ Error in {path}: {e}")
#         continue


import shutil, os
import pandas as pd
from pathlib import Path

# ───── VOCALS ─────
taken_acronym = '2556'
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