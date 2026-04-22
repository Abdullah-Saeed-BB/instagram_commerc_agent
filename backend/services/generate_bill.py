from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

def generate_bill(
        filename, barber_name, booking_datetime,
        service_name, price, payment_status,
        customer_name, booking_id):
    # 1. Define custom width and calculate dynamic height
    # Total width is 4 inches, height depends on content (approx 6 inches for this layout)
    custom_width = 4.5 * inch
    custom_height = 6.5 * inch
    
    # Use top and bottom margin of 0.2 inch to keep it tight
    doc = SimpleDocTemplate(
        filename, 
        pagesize=(custom_width, custom_height),
        rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20
    )
    
    styles = getSampleStyleSheet()
    elements = []

    # --- Section 1: Logo and Brand ---
    try:
        logo_path = "static/images/logo.png"
        logo = Image(logo_path, width=0.8*inch, height=0.8*inch)
        elements.append(logo)
    except:
        elements.append(Paragraph("<b>[LOGO]</b>", styles['Title']))

    brand_style = ParagraphStyle('BrandStyle', parent=styles['Title'], alignment=TA_CENTER, fontSize=18)
    elements.append(Paragraph("SILVER BLADE", brand_style))
    elements.append(Spacer(1, 0.2 * inch))

    # --- Section 2 & 3: Information (Stacked Label/Value) ---
    # Helper to format the "Bold Label \n Value" style
    def format_cell(label, value):
        return Paragraph(f"<b>{label.upper()}</b><br/>{value}", styles['Normal'])

    # Each row contains two "cells", but each cell has a label and a value on a new line
    table_data = [
        [format_cell("Barber", barber_name), format_cell("Date", booking_datetime)],
        [format_cell("Service", service_name), format_cell("Price", price)],
        [format_cell("Status", payment_status), format_cell("Customer", customer_name)]
    ]

    # Increased table width to 4 inches total
    table = Table(table_data, colWidths=[2 * inch, 2 * inch])
    
    table.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 15), # Space between rows
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        # Set border color to white (same as background) to "remove" it
        ('GRID', (0, 0), (-1, -1), 0.5, colors.white), 
    ]))
    
    elements.append(table)
    elements.append(Spacer(1, 0.3 * inch))

    # --- Section 4: Barcode ---
    booking_id = str(booking_id)
    code128 = barcode.get('code128', booking_id, writer=ImageWriter())
    barcode_buffer = BytesIO()
    code128.write(barcode_buffer)
    barcode_buffer.seek(0)

    barcode_img = Image(barcode_buffer, width=3.2 * inch, height=0.8 * inch)
    barcode_img.hAlign = 'CENTER'
    elements.append(barcode_img)
    
    id_style = ParagraphStyle('IDStyle', parent=styles['Normal'], alignment=TA_CENTER, fontSize=10)
    elements.append(Paragraph(f"ID: {booking_id}", id_style))

    # Build the PDF
    doc.build(elements)

# from reportlab.lib.pagesizes import letter
# from reportlab.lib.units import inch
# from reportlab.lib import colors
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Image, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
# from reportlab.lib.enums import TA_CENTER
# from reportlab.lib.utils import ImageReader
# import barcode
# from barcode.writer import ImageWriter
# from io import BytesIO



# def generate_bill(
#         filename, barber_name, booking_datetime,
#         service_name, price, payment_status,
#         customer_name, booking_id):
#     doc = SimpleDocTemplate(filename, pagesize=letter)
#     styles = getSampleStyleSheet()
#     elements = []

#     # --- Section 1: Logo and Brand (Centered) ---
#     try:
#         logo_path = "static/images/logo.png"
#         logo = Image(logo_path, width=1*inch, height=1*inch)
#         elements.append(logo)
#     except:
#         # Fallback if logo file doesn't exist yet
#         elements.append(Paragraph("<b>[LOGO]</b>", styles['Title']))

#     brand_style = ParagraphStyle('BrandStyle', parent=styles['Title'], alignment=TA_CENTER)
#     elements.append(Paragraph("Silver Blade", brand_style))
#     elements.append(Spacer(1, 0.3 * inch))

#     # --- Section 2 & 3: Ticket Information (Table Layout) ---
#     # We arrange data in 2 columns per row
#     ticket_info = [
#         [f"Barber: {barber_name}", f"Date: {booking_datetime}"],
#         [f"Service: {service_name}", f"Price: {price}"],
#         [f"Status: {payment_status}", f"Customer: {customer_name}"]
#     ]

#     table = Table(ticket_info, colWidths=[2.5 * inch, 2.5 * inch])
#     table.setStyle(TableStyle([
#         ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
#         ('FONTSIZE', (0, 0), (-1, -1), 11),
#         ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
#         ('GRID', (0, 0), (-1, -1), 0.5, colors.grey), # Optional: remove for a cleaner look
#         ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#     ]))
#     elements.append(table)
#     elements.append(Spacer(1, 0.4 * inch))

#     # --- Section 4: Barcode and ID ---
#     # Generate Barcode
#     booking_id = str(booking_id)
#     code128 = barcode.get('code128', booking_id, writer=ImageWriter())
#     barcode_buffer = BytesIO()
#     code128.write(barcode_buffer)
#     barcode_buffer.seek(0)

#     # Use ImageReader for the buffer
#     barcode_img = Image(barcode_buffer, width=3 * inch, height=1 * inch)
#     barcode_img.hAlign = 'CENTER'
#     elements.append(barcode_img)
    
#     id_style = ParagraphStyle('IDStyle', parent=styles['Normal'], alignment=TA_CENTER)
#     elements.append(Paragraph(f"ID: {booking_id}", id_style))

#     # Build the PDF
#     doc.build(elements)
#     print(f"Ticket saved as {filename}")
