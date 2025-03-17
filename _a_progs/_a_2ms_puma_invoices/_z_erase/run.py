################always start 
#which python

import sys
print(sys.executable)

############# functions 
# import subprocess
# subprocess.run(["python3", "_0_fns/_invoice_fn_.py"])
import sys
sys.path.append("_0_fns")  # Add the directory to the Python path

from _invoice_fn_ import create_invoice  # Import the function directly

################ RUN

# -----######-----###### FUNCTION START -----######-----######

def _invoice_0305_dj_dinner_SET_GET_invoice():
    """
    This function prompts the user for an invoice number and service date (mm/dd/yyyy),
    formats them, and then generates an invoice.
    """
    # Prompt user for required inputs
    invoice_number = input("Enter Invoice Number: ").strip()
    date_of_service = input("Enter Date of Service (mm/dd/yyyy): ").strip()

    # Validate date format
    try:
        from datetime import datetime
        datetime.strptime(date_of_service, "%m/%d/%Y")  # Ensure valid format
    except ValueError:
        print("Invalid date format. Please enter in mm/dd/yyyy format.")
        return

    # Generate today's date
    from datetime import date
    date_sent_invoice = date.today().strftime("%m/%d/%Y")

    # Static parameters
    yr_code = date.today().strftime("%y")  # Extract last two digits of the year
    gral_service_fee = 0
    additional_amount = 0
    due_date = "Within 3-5 days"
    subject_matter = "Dj_Dinner_SET"
    time_slot_night = "6pm-10pm"
    event_rate = "250"

    # Generate invoice
    create_invoice(
        due_date=due_date,
        invoice_number=f"ac-{yr_code}-{invoice_number}",
        invoice_date=date_sent_invoice,
        service_date=date_of_service,
        dj_name=subject_matter,
        time_slot=time_slot_night,
        rate=event_rate,
        additional_amount=additional_amount,
        service_fee=gral_service_fee
    )

# -----######-----###### FUNCTION END -----######-----######

# !#!#!#!#! RUNNING STATEMENTS !#!#!#!#! 
_invoice_0305_dj_dinner_SET_GET_invoice()
