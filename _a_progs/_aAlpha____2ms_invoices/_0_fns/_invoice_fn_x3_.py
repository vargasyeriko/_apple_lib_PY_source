# -----######-----######-----######-----######-----
# Weekly Puma Invoice (Fri, Sat, Mon) – Fixed $800 total (DIR-FIX)
# -----######-----######-----######-----######-----

import os, sys, glob
from datetime import datetime, date, timedelta
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from PIL import Image as PILImage

# ---------- TQM ----------
def _tqm_bar(label, total_steps):
    width = 30
    def _update(step_idx):
        done = int((step_idx / total_steps) * width)
        bar = "█" * done + " " * (width - done)
        pct = int((step_idx / total_steps) * 100)
        sys.stdout.write(f"\rTQM | {label}: {pct:3d}%|{bar}| {step_idx}/{total_steps}")
        sys.stdout.flush()
        if step_idx == total_steps:
            sys.stdout.write("\n")
    return _update

# ---------- Helpers ----------
def _safe_bw_outpath(original_path, out_dir="pics"):
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.basename(original_path)
    name, ext = os.path.splitext(base)
    return os.path.join(out_dir, f"bw_{name}{ext}")

def _convert_image_to_bw(image_path, out_path=None):
    if not image_path:
        return None
    try:
        if out_path is None:
            out_path = _safe_bw_outpath(image_path)
        img = PILImage.open(image_path).convert('L')
        img.save(out_path)
        return out_path
    except Exception:
        return None

def _parse_mmddyyyy(s):
    return datetime.strptime(s.strip(), "%m/%d/%Y").date()

def _fmt_mmddyyyy(d):
    return d.strftime("%m/%d/%Y")

def _week_dates_from_monday(monday_date):
    friday  = monday_date - timedelta(days=3)
    saturday= monday_date - timedelta(days=2)
    return monday_date, saturday, friday

def _resolve_invoice_dir(invoice_dir):
    """
    Priority:
      1) explicit param if provided
      2) env var INVOICE_DIR
      3) nearest ./_1a_dta_invoices under CWD (auto-create)
      4) your Alpha path (this project)
    """
    # 1) explicit param
    if invoice_dir:
        os.makedirs(invoice_dir, exist_ok=True)
        return invoice_dir

    # 2) env var
    env_dir = os.environ.get("INVOICE_DIR", "").strip()
    if env_dir:
        os.makedirs(env_dir, exist_ok=True)
        return env_dir

    # 3) nearest folder under CWD
    cwd_dir = os.path.join(os.getcwd(), "_1a_dta_invoices")
    try:
        os.makedirs(cwd_dir, exist_ok=True)
        return cwd_dir
    except Exception:
        pass

    # 4) fallback: your Alpha project path
    alpha_dir = "/Users/yerik/_apple_lib/_a_progs/_aAlpha____2ms_invoices/_1a_dta_invoices"
    os.makedirs(alpha_dir, exist_ok=True)
    return alpha_dir

# -----######-----######  CORE IMPORTABLE FN  -----######-----######
def _invoice_1609_weekly_SET_GET_invoice(
    *,
    invoice_dir=None,  # <-- now optional; auto-resolves to Alpha path if not set
    logo_path="pics/logo.png",
    payment_image_path="_2_pics/method_paym.jpg",
    venmo_handle="",
    cashapp_handle="",
    zelle_text="",
    time_slot="6pm-10pm",
):
    """
    Interactive 3-day invoice (Mon/Sat/Fri) with fixed weekly total=$800.
    Prompts:
      - Invoice Number (becomes invoice_ac-YY-##.pdf)
      - Monday Date (MM/DD/YYYY)
    Saves by default to:
      /Users/yerik/_apple_lib/_a_progs/_aAlpha____2ms_invoices/_1a_dta_invoices
    unless overridden by `invoice_dir` or $INVOICE_DIR, or a local ./_1a_dta_invoices exists.
    """
    tqm = _tqm_bar("Weekly Puma Invoice", 7)

    # 1) Inputs
    invoice_number_raw = input("Enter Invoice Number: ").strip()
    monday_str = input("Enter Monday Date (mm/dd/yyyy): ").strip()
    tqm(1)

    # 2) Validate & compute dates
    try:
        monday_date = _parse_mmddyyyy(monday_str)
    except Exception:
        print("\n❌ Invalid date format. Use mm/dd/yyyy.")
        sys.exit(1)
    if monday_date.weekday() != 0:
        print("⚠️ Provided date is not a Monday; proceeding relative to it.")
    mon, sat, fri = _week_dates_from_monday(monday_date)
    tqm(2)

    # 3) Rates enforcing $800
    night_rates = {"Friday": 266.0, "Saturday": 268.0, "Monday": 266.0}
    subtotal = night_rates["Friday"] + night_rates["Saturday"] + night_rates["Monday"]
    if round(subtotal, 2) != 800.00:
        night_rates["Monday"] = round(800.00 - (night_rates["Friday"] + night_rates["Saturday"]), 2)

    services = [
        (_fmt_mmddyyyy(mon), "DJ-bookings", time_slot, night_rates["Monday"]),
        (_fmt_mmddyyyy(sat), "DJ-bookings", time_slot, night_rates["Saturday"]),
        (_fmt_mmddyyyy(fri), "DJ-bookings", time_slot, night_rates["Friday"]),
    ]
    tqm(3)

    # 4) Resolve output dir (NEW)
    out_dir = _resolve_invoice_dir(invoice_dir)
    tqm(4)

    # 5) Output path + collision guard
    yr_code = date.today().strftime("%y")
    pdf_filename = f"invoice_ac-{yr_code}-{invoice_number_raw}.pdf"
    out_path = os.path.join(out_dir, pdf_filename)
    if os.path.exists(out_path):
        print(f"\n🚨 Invoice '{pdf_filename}' already exists in:\n{out_dir}\n❌ Aborting to prevent overwrite. Choose another number.\n")
        sys.exit(1)
    tqm(5)

    # 6) Render PDF
    _create_invoice_weekly_pdf(
        pdf_path=out_path,
        invoice_number=f"ac-{yr_code}-{invoice_number_raw}",
        invoice_date=date.today().strftime("%m/%d/%Y"),
        due_date="Within 3-5 days",
        services=services,
        logo_path=logo_path,
        payment_image_path=payment_image_path,
        venmo_handle=venmo_handle,
        cashapp_handle=cashapp_handle,
        zelle_text=zelle_text,
    )
    tqm(6)

    print(f"✅ Invoice saved as: {out_path}")
    tqm(7)

# ---------- Internal renderer ----------
def _create_invoice_weekly_pdf(
    *,
    pdf_path,
    invoice_number,
    invoice_date,
    due_date,
    services,
    logo_path,
    payment_image_path,
    venmo_handle,
    cashapp_handle,
    zelle_text,
):
    subtotal = round(sum(row[3] for row in services), 2)
    additional_amount = 0.0
    service_fee = 0.0
    total_due_amount = round(subtotal + additional_amount + service_fee, 2)

    doc = SimpleDocTemplate(pdf_path, pagesize=letter)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Center', alignment=1))

    elems = []
    # Header
    company_info = [
        Paragraph("YerikoDJ-bookings", styles['Title']),
        Paragraph("Email: ygvargas93@gmail.com", styles['Normal']),
        Paragraph("Phone Number: (646) 771-6111", styles['Normal'])
    ]
    try:
        logo = Image(logo_path); logo.drawHeight = 1*inch; logo.drawWidth = 1*inch
        header_tbl = Table([[company_info, logo]], colWidths=[4*inch, 1*inch])
    except Exception:
        header_tbl = Table([[company_info, Paragraph("", styles['Normal'])]], colWidths=[5*inch, 0*inch])
    header_tbl.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP')
    ]))
    elems += [header_tbl, Spacer(1, 0.35*inch)]

    # Meta
    elems += [
        Paragraph(f"Invoice #: {invoice_number}", styles['Normal']),
        Paragraph(f"Date: {invoice_date}", styles['Normal']),
        Paragraph(f"Due Date: {due_date}", styles['Normal']),
        Spacer(1, 0.2*inch),
        Paragraph("Bill To: Javier Bardauil, Owner of Puma", styles['Normal']),
        Paragraph("4725 16th St", styles['Normal']),
        Paragraph("Detroit, MI 48208", styles['Normal']),
        Paragraph("United States", styles['Normal']),
        Paragraph("Email: javier@pumadetroit.com", styles['Normal']),
        Paragraph("Phone Number: (248) 949-3330", styles['Normal']),
        Spacer(1, 0.3*inch),
    ]

    # Table
    data = [["Date", "Service", "Time Slot", "Amount"]]
    for d, desc, ts, amt in services:
        data.append([d, desc, ts, f"${amt:,.2f}"])
    tbl = Table(data, colWidths=[1.3*inch, 2.4*inch, 1.5*inch, 1.2*inch])
    tbl.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('GRID', (0,0), (-1,-1), 1, colors.black),
    ]))
    elems += [Paragraph("Description of Services:", styles['Normal']), Spacer(1, 0.12*inch), tbl, Spacer(1, 0.3*inch)]

    # Financials
    elems += [
        Paragraph(f"Subtotal: ${subtotal:,.2f}", styles['Normal']),
        Paragraph(f"Additional: ${0.0:,.2f}", styles['Normal']),
        Paragraph(f"Service Fee: ${0.0:,.2f}", styles['Normal']),
        Paragraph(f"<b>Total Due: ${total_due_amount:,.2f}</b>", styles['Normal']),
        Spacer(1, 0.3*inch)
    ]

    # Payment
    elems += [Paragraph("Payment Instructions:", styles['Normal']), Paragraph("Please make payment to:", styles['Normal'])]
    for line in (f"Venmo (preferred): {venmo_handle}", f"Cash App: {cashapp_handle}", f"{zelle_text}"):
        elems.append(Paragraph(line, styles['Normal']))

    bw_path = _convert_image_to_bw(payment_image_path)
    if bw_path:
        try:
            pay_img = Image(bw_path); pay_img.drawHeight = 2*inch; pay_img.drawWidth = 4*inch
            elems += [Spacer(1, 0.18*inch), pay_img]
        except Exception:
            pass

    elems += [
        Spacer(1, 0.3*inch),
        Paragraph("Notes:", styles['Normal']),
        Paragraph("Payment is due within 3–5 days of the invoice date.", styles['Normal']),
        Paragraph("Accepted Payment Methods: Venmo [preferred], Cash App, & Zelle.", styles['Normal']),
        Spacer(1, 0.3*inch),
        Paragraph("Thank you for your business!", styles['Center']),
    ]

    doc.build(elems)

# ---------- Back-compat alias ----------
def _invoice_PUMA_dj_dinner_SET_GET_invoice_3days(**kwargs):
    return _invoice_1609_weekly_SET_GET_invoice(**kwargs)
