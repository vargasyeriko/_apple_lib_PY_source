import os, importlib.util, sys, re

BASE = os.getcwd()
PROGS_DIR = os.path.join(BASE, "_1_progs")

def get_programs():
    """
    Returns {program_number:int : full_path:str}
    Extracts the FIRST integer found in the filename.
    """
    programs = {}
    for f in os.listdir(PROGS_DIR):
        if f.startswith("_") and f.endswith(".py"):
            match = re.search(r"_(\d+)_", f)
            if match:
                num = int(match.group(1))
                programs[num] = os.path.join(PROGS_DIR, f)
    return dict(sorted(programs.items()))

def run_file(path):
    name = os.path.basename(path)
    try:
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
    except Exception as e:
        print(f"\n❌ ERROR: Failed to load {name}\n{e}")
        return

    if hasattr(mod, "main"):
        print(f"\n▶️  Running: {name}\n")
        try:
            mod.main()
        except Exception as e:
            print(f"\n❌ ERROR inside main() of {name}\n{e}")
    else:
        print(f"\n⚠️ WARNING: {name} has NO main() function.\n")


if __name__ == "__main__":
    if not os.path.exists(PROGS_DIR):
        print("❌ ERROR: Folder '_1_progs' not found.")
        sys.exit()

    programs = get_programs()

    if not programs:
        print("❌ ERROR: No valid programs found in _1_progs.")
        sys.exit()

    print("\n============================")
    print("       AVAILABLE PROGRAMS")
    print("============================")
    for k, v in programs.items():
        print(f" {k} → {os.path.basename(v)}")
    print("============================")

    choice = input("Run program # → ").strip()

    if not choice.isdigit():
        print("\n❌ ERROR: You must enter a number.")
        sys.exit()

    choice = int(choice)

    if choice not in programs:
        print(f"\n❌ ERROR: Program #{choice} does not exist.")
        sys.exit()

    run_file(programs[choice])
