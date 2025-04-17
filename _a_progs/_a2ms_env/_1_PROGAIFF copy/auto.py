folder_list = ['/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_02_AN_LA_VENTANA',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_03_Love_Lang',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_04_Foundation_Hotel',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_04_NEW_LODGE',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_05_AN_bigPINK',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_06_ttt_SPKRBOX',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_08_Barefoot',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_08_SL_ACAPELLAS',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_09_AN_ArtPArk',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_10_Detroit_Hou_Tech',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_11_AN_SpotLite',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2023_this/_23_12_Tangent_Debout',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_04_BBssBBssBBs_BandCamp',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_04_NorthL_BadBunny_LatinFast',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_05_MVMNT_block_is_HOT',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_06_Detroit_Brazil_Funky',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_06_Metroplex_1_and_RNDMgood',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_06_Metroplex_2_and_RNDMgood',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_07_Puma_BurningMan_indian',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_08_Barefoot_and_FREE',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_08_Xime_13_Memorial',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_09_Eagle_SPKR_Techno',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_09_Ghettotech_HiTECH_stu',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_11_11_N0_Supervisi0n_SPKRbox',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_11_11_albm_LordECHO_JAZZ',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_11_11_albm_MimSuleiman_TRIBAL',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_11_Dinner_Materia_Puma_Jazzy',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_12_Dinner_HipHop_Indian_Puma',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_12_NYE_25',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/__24_12_fixed_and_added',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/___DJ_friends_Nun',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2024_this/___YODJ_N0Supervisi0n',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_02_CDMX_SecretoRoom',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_02_DETROIT_PUMA_SPKR',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_03_CAPSULE_House_Latin',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_04_BCAL_SalsaEstrellasPa',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_04_BCAL_TerapiaLatina',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_04_BP_LATIN_HOUSE',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_04_BP_Rapharazzi_BDAY',
 '/Volumes/MUSIC_PROD/_1_NEW_SOURCE_this/_2025_this/__25_04_BP_ximMAYBDAY_HOUSY_PARTY_LATIN']

counter = 0

for path in folder_list:
    try:
        print(f"\n🔁 Processing: {path}")
        my_aiff = path
        direc_jpg = "images/"
        direc_tables = "tables/"

        # Execute external script
        exec(open("run.py", encoding="utf-8").read())

        # Save first row of df using custom file name format
        pkl_name = f"df_{counter:03d}_.pkl"
        df.to_pickle(pkl_name)
        print(f"✅ Saved: {pkl_name}")
        [shutil.rmtree(f, ignore_errors=True) or os.makedirs(f, exist_ok=True) for f in ['images/', 'tables/']]
        print('images and tables folders erased')
        counter += 1

    except Exception as e:
        print(f"❌ Error in {path}: {e}")
        continue
