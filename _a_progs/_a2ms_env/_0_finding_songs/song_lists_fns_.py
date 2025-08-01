# -----######-----###### TRACKLIST CLEANER + VALIDATOR + OVERWRITER -----######-----######
from importlib import reload
import song_lists
from pathlib import Path
import json

def validate_and_clean_songlists(overwrite=False, verbose=True):
    reload(song_lists)
    all_lists = [(k, v) for k, v in vars(song_lists).items() if k.startswith("list_") and isinstance(v, list)]
    
    if not all_lists:
        print("❌ No track lists found (list_1, list_2, etc).")
        return None

    print(f"\n📦 Found {len(all_lists)} lists:")
    for name, lst in all_lists:
        print(f"   - {name}: {len(lst)} tracks")

    seen = set()
    duplicates = []
    invalids = []
    cleaned_lists = {}
    all_combined = []

    for name, tracklist in all_lists:
        cleaned = []
        for track in tracklist:
            if not isinstance(track, dict):
                invalids.append({"error": "❌ Not a dictionary", "track": track})
                continue
            title = track.get("title", "").strip()
            artist = track.get("artist", "").strip()
            if not title or not artist:
                invalids.append({"error": "❌ Missing title or artist", "track": track})
                continue
            key = (title.lower(), artist.lower())
            if key in seen:
                duplicates.append(track)
                continue
            seen.add(key)
            cleaned.append(track)
            all_combined.append(track)
        cleaned_lists[name] = cleaned

    print("\n🧹 Tracklist Cleanup Summary")
    print(f"🎧 Total track entries:      {sum(len(v) for _, v in all_lists)}")
    print(f"✅ Valid & unique entries:   {len(seen)}")
    print(f"🔁 Duplicate entries removed: {len(duplicates)}")
    print(f"⚠️  Invalid entries removed:  {len(invalids)}")

    if verbose:
        if invalids:
            print("\n⚠️  Invalids:")
            for i in invalids[:5]:
                print(f"- {i['error']}: {i['track']}")
        if duplicates:
            print("\n🔁 Duplicates:")
            for d in duplicates[:5]:
                print(f"- {d['title']} by {d['artist']}")

    if overwrite:
        out_path = Path(song_lists.__file__)
        lines = ["# Auto-cleaned track lists\n"]
        for name, lst in cleaned_lists.items():
            json_str = json.dumps(lst, indent=4, ensure_ascii=False)
            lines.append(f"{name} = {json_str}\n")
        out_path.write_text("\n".join(lines), encoding='utf-8')
        print(f"\n✅ Cleaned version saved to → {out_path}")

    return {
        "all_tracks": len(all_combined),
        "duplicates": duplicates,
        "invalids": invalids,
        "valid_count": len(seen)
    }


### open fn 
# -----######-----###### TRACK LOOP w/ AUTO COMBINE + SAVE-ON-SELECT -----######-----######
import webbrowser
import pandas as pd
import os

def play_track_search_loop():
    # Collect all list_# that exist in the global scope
    all_lists = [v for k, v in globals().items() if k.startswith("list_") and isinstance(v, list)]
    if not all_lists:
        print("❌ No track lists found (list_1, list_2, etc).")
        return

    track_list = []
    for lst in all_lists:
        track_list.extend(lst)

    # ✅ LOAD ALREADY SAVED SONGS TO SKIP
    saved_keys = set()
    df_saved = pd.DataFrame()
    if os.path.exists("df_might_buy.csv"):
        try:
            df_saved = pd.read_csv("df_might_buy.csv")
            saved_keys = {(row["title"], row["artist"]) for _, row in df_saved.iterrows()}
            print(f"🛑 Skipping {len(saved_keys)} previously saved tracks from df_might_buy.csv")
        except Exception as e:
            print(f"⚠️ Error reading df_might_buy.csv: {e}")

    print(f"\n🎧 Loaded {len(track_list)} total tracks from {len(all_lists)} lists.\n")

    search_results = []
    might_buy = []

    for i, track in enumerate(track_list, 1):
        title = track["title"]
        artist = track["artist"]
        remixer = track.get("remixer", "")
        bpm = track.get("bpm", "?")

        # ✅ SKIP IF ALREADY SAVED
        if (title, artist) in saved_keys:
            continue

        print(f"\n#{i}")
        print(f"🎶 Song:     {title}")
        print(f"👤 Artist:   {artist}")
        if remixer:
            print(f"🎛️ Remixer:  {remixer}")
        print(f"🎚️ BPM:      {bpm}")

        query = f"{artist} {title}"
        if remixer:
            query += f" {remixer}"
        query += " beatport bandcamp"
        url = f"https://www.google.com/search?q={query.replace(' ', '+')}"

        user_input = input("➡️  Press Enter to open, or 'n' to skip: ").strip().lower()
        if user_input == "n":
            search_results.append(track)
            continue

        # Try Chrome, fallback to default
        try:
            webbrowser.get("chrome").open(url)
        except:
            webbrowser.open(url)

        decision = input("💾 Did you save it to buy later? Press 's' to save, Enter to continue: ").strip().lower()
        if decision == "s":
            might_buy.append(track)

            # ✅ APPEND TO df_might_buy.csv SAFELY
            df_new = pd.DataFrame(might_buy)
            if not df_saved.empty:
                df_combined = pd.concat([df_saved, df_new], ignore_index=True)
                df_combined.drop_duplicates(subset=["title", "artist"], inplace=True)
            else:
                df_combined = df_new
            df_combined.to_csv("df_might_buy.csv", index=False)
            print("💾 Appended → df_might_buy.csv")

            # Update memory state so you don't save again
            saved_keys.add((title, artist))
            df_saved = df_combined.copy()

        else:
            search_results.append(track)

    df_search_songs = pd.DataFrame(search_results)
    print("\n✅ Done!")
    print(f"🔍 Still searching: {len(df_search_songs)}")
    print(f"💸 Total saved to buy: {len(df_saved)}")

    return df_search_songs

