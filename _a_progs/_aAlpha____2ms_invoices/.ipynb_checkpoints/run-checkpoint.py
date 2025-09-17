# -----######-----######-----######-----######-----
# Controller: Choose between Single-Day or Three-Day Invoices
# -----######-----######-----######-----######-----

import sys
import subprocess

def _invoice_choice_controller_RUN():
    """
    Ask user if they want to run a single-day (runx1.py) or a three-day (runx3.py) invoice.
    Runs the corresponding script.
    """
    print("\n--- Puma Invoice Generator ---")
    print("1. Single-Day Invoice")
    print("2. Three-Day Weekly Invoice\n")

    choice = input("Enter choice (1 or 2): ").strip()

    if choice == "1":
        print("\n➡️ Running Single-Day Invoice (runx1.py)...\n")
        subprocess.run([sys.executable, "runx1.py"])
    elif choice == "2":
        print("\n➡️ Running Three-Day Invoice (runx3.py)...\n")
        subprocess.run([sys.executable, "runx3.py"])
    else:
        print("❌ Invalid choice. Please enter 1 or 2.")

_invoice_choice_controller_RUN()