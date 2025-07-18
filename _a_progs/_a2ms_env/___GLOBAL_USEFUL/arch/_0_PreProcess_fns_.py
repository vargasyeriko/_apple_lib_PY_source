# ----------------------------######----------------------------#
#   _rename_1307_kwtagging_GET_singlefile_interactive          #
# ----------------------------######----------------------------#

import os
from datetime import datetime

def _rename_1307_kwtagging_GET_singlefile_interactive(file_path):
    """
    Interactively renames a single audio file with keyword-tagged structure.
    Uses filename as default title and asks user which fields to override.
    """

    if not os.path.isfile(file_path):
        print("❌ File not found.")
        return None

    def clean(s):
        return (
            str(s)
            .replace(" ", "_").replace("/", "___").replace(",", "_")
            .replace("(", "").replace(")", "").replace("!", "")
            .replace("&", "and").replace("’", "").replace("'", "")
            .replace("¿", "").replace("¡", "").replace(":", "")
            .replace(";", "").strip()
        )

    def ask_override(field_name, default=""):
        choice = input(f"🔧 Do you want to override '{field_name}'? (y/n): ").lower()
        return input(f"👉 Enter value for {field_name}: ") if choice == 'y' else default

    base_name = os.path.splitext(os.path.basename(file_path))[0]
    ext = os.path.splitext(file_path)[1]

    print(f"\n🎵 Default Track Title: {base_name}\n")

    overrides = {
        "Track Title": base_name,
        "Artist": "Unknown",
        "Mix Type": "original",
        "Key": "NA",
        "BPM": "NA",
        "Genre": "NA",
        "Label": "NA",
        "Release Date": "NA",
        "Purchase Date": datetime.today().strftime('%Y_%m_%d')
    }

    options_list = list(overrides.keys())
    for i, field in enumerate(options_list):
        print(f"{i+1}. {field}")

    while True:
        modify = input("\n🔁 Enter numbers of fields to override (comma-separated), or 'n' to skip: ").strip()
        if modify.lower() == 'n':
            break
        selected_fields = [int(i)-1 for i in modify.split(",") if i.strip().isdigit()]
        for idx in selected_fields:
            if 0 <= idx < len(options_list):
                field = options_list[idx]
                val = ask_override(field, overrides[field])
                overrides[field] = clean(val)
        confirm = input("✅ Done editing? (y/n): ").lower()
        if confirm == 'y':
            break

    # Build new filename
    new_name = (
        f"TRkw_{overrides['Track Title'][:25]}"
        f"_ARkw_{overrides['Artist'][:25]}"
        f"_MXkw_{overrides['Mix Type']}"
        f"_KYkw_{overrides['Key']}"
        f"_BPkw_{overrides['BPM']}"
        f"_GNkw_{overrides['Genre']}"
        f"_LBkw_{overrides['Label']}"
        f"_RYkw_{overrides['Release Date']}"
        f"_PYkw_{overrides['Purchase Date']}{ext}"
    )

    if len(new_name) > 240:
        new_name = new_name[:230] + ext

    new_path = os.path.join(os.path.dirname(file_path), new_name)
    try:
        os.rename(file_path, new_path)
        print(f"\n✅ Renamed to: {new_name}")
        return new_path
    except Exception as e:
        print(f"❌ Rename failed: {e}")
        return None
