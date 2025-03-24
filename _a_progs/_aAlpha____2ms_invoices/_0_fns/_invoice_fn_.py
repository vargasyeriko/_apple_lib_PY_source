from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from PIL import Image as PILImage


######### DATE FN

# -----######-----######-----######-----######-----
# Function to Get Today's Date
# -----######-----######-----######-----######-----

def _date_GET_todays_date():
    """
    Returns today's date in the format MM/DD/YYYY.
    If the system date is not available, prompts the user to input the date.
    """
    import datetime

    try:
        # Attempt to get the current date
        today = datetime.date.today().strftime("%m/%d/%Y")
    except Exception as e:
        print("Unable to retrieve the system date.")
        print("Please input today's date in the format MM/DD/YYYY:")
        today = input("today = ").strip()

        # Validate the user input
        try:
            datetime.datetime.strptime(today, "%m/%d/%Y")
        except ValueError:
            raise ValueError("Invalid date format. Please use MM/DD/YYYY.")
    
    return today


######### INVOICE FN

def convert_image_to_bw(image_path):
    """
    Convert an image to black and white.

    Args:
        image_path (str): Path to the original image.

    Returns:
        str: Path to the black and white image.
    """
    img = PILImage.open(image_path).convert('L')
    bw_image_path = "pics/bw_" + image_path.split('/')[-1]
    img.save(bw_image_path)
    return bw_image_path

def create_invoice(invoice_number,
                   invoice_date, 
                   service_date, 
                   dj_name, 
                   time_slot, 
                   rate, 
                   additional_amount, 
                   service_fee, 
                   due_date,
                   venmo_handle="@yerikodj",  # example Venmo handle
                   cashapp_handle="$yerikodj",
                   payment_image_path="_2_pics/method_paym.jpg",
                   logo_path = "pics/logo.png" ):
    """
    Create a professional invoice PDF.

    Args:
        invoice_number (str): Invoice number.
        invoice_date (str): Date of the invoice.
        service_date (str): Date of the service.
        dj_name (str): Name of the DJ.
        time_slot (str): Time slot of the service.
        rate (str): Base rate for the service.
        additional_amount (float): Additional amount from bar sales.
        service_fee (float): Service fee.
        venmo_handle (str): Venmo handle for payment.
        cashapp_handle (str): Cash App handle for payment.
        payment_image_path (str): Path to the payment methods image.
        logo_path (str): Path to the company logo.
    """
    # Calculate total amounts
    base_rate = float(rate)
    total_due_amount = base_rate + additional_amount + service_fee

    # Create a PDF document
    pdf_filename = f"_1a_dta_invoices/invoice_{invoice_number}.pdf"
    doc = SimpleDocTemplate(pdf_filename, pagesize=letter)

    # Styles
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))

    # Elements to add to PDF
    elements = []

    # Add company information with logo in the right corner
    company_info = [
        Paragraph("YerikoDJ-bookings", styles['Title']),
        Paragraph("Email: ygvargas93@gmail.com", styles['Normal']),
        Paragraph("Phone Number: (646) 771-6111", styles['Normal'])
    ]
    logo = Image(logo_path)
    logo.drawHeight = 1 * inch  # Set logo height
    logo.drawWidth = 1 * inch  # Set logo width

    # Create a table to position the logo in the upper right corner
    company_info_table = Table(
        [
            [company_info, logo]
        ],
        colWidths=[4 * inch, 1 * inch]
    )
    company_info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, 0), 'LEFT'),
        ('ALIGN', (1, 0), (1, 0), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ]))
    elements.append(company_info_table)
    elements.append(Spacer(1, 0.5 * inch))

    # Invoice Information
    elements.append(Paragraph(f"Invoice #: {invoice_number}", styles['Normal']))
    elements.append(Paragraph(f"Date: {invoice_date}", styles['Normal']))
    elements.append(Paragraph(f"Due Date: {due_date}", styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    # Billing Information
    elements.append(Paragraph("Bill To: Javier Bardauil, Owner of Puma", styles['Normal']))
    elements.append(Paragraph("4725 16th St", styles['Normal']))
    elements.append(Paragraph("Detroit, MI 48208", styles['Normal']))
    elements.append(Paragraph("United States", styles['Normal']))
    elements.append(Paragraph("Email: javier@pumadetroit.com", styles['Normal']))
    elements.append(Paragraph("Phone Number: (248) 949-3330", styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Services Description
    elements.append(Paragraph("Description of Services:", styles['Normal']))
    elements.append(Spacer(1, 0.25 * inch))

    data = [
        ["Date", "DJ-bookings", "Time Slot", "Rate", "Total Amount"],
        [service_date, dj_name, time_slot, f"${rate}", f"${base_rate:.2f}"]
    ]
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # Financial Summary
    elements.append(Paragraph(f"Base Rate: ${base_rate:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Additional % ${additional_amount:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Service Fee: ${service_fee:.2f}", styles['Normal']))
    elements.append(Paragraph(f"Total Due: ${total_due_amount:.2f}", styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Payment Instructions
    elements.append(Paragraph("Payment Instructions:", styles['Normal']))
    elements.append(Paragraph("Please make payment to:", styles['Normal']))

    # Add payment methods image
    bw_image_path = convert_image_to_bw(payment_image_path)
    payment_image = Image(bw_image_path)
    payment_image.drawHeight = 2 * inch
    payment_image.drawWidth = 4 * inch
    elements.append(payment_image)
    elements.append(Spacer(1, 0.5 * inch))

    # Notes
    elements.append(Paragraph("Notes:", styles['Normal']))
    elements.append(Paragraph("Payment is due within 3-5 days of the invoice date.", styles['Normal']))
    elements.append(Paragraph("Accepted Payment Methods: Venmo [preferred], Cash App, & Zelle. ", styles['Normal']))
    elements.append(Spacer(1, 0.5 * inch))

    # Legal Disclaimers
    
    elements.append(Spacer(1, 0.5 * inch))

    # Thank You Note
    elements.append(Paragraph("Thank you for your business!", styles['Center']))

    # Build PDF
    doc.build(elements)

    print(f"Invoice saved as {pdf_filename}")



    
    
# ########### RUN

# date_sent_invoice = _date_GET_todays_date() # date for sending it = TODAY !

# # # RUN - > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > > >
# create_invoice(
#     due_date=due_date, # # OR = 'paid'
#     invoice_number=f"ac-{yr_code}-{invoice_number}", # invoice Number
#     ###DATES
#     invoice_date= date_sent_invoice, # # date for sending it!
#     service_date= date_of_service, # -------------> SERVCE DATE
#     dj_name= subject_matter,
#     time_slot=time_slot_night,
#     rate=event_rate,
#     additional_amount=additional_amount,  # example additional amount from bar sales
#     service_fee= gral_service_fee  # example service fee
# )