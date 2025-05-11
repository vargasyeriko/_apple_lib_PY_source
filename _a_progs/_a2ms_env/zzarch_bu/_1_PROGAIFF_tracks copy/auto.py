folder_list = ['/Users/yerik/Desktop/test/1', '/Users/yerik/Desktop/test/2']
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
