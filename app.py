import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os

st.title("MUNA Georgia Sponsors Invoice")

# -------- Invoice Number Generator --------
def generate_invoice_number():
    year = datetime.now().year
    counter_file = "invoice_counter.txt"

    if not os.path.exists(counter_file):
        with open(counter_file, "w") as f:
            f.write("1")

    with open(counter_file, "r") as f:
        count = int(f.read())

    invoice_number = f"{year}{count:03d}"

    with open(counter_file, "w") as f:
        f.write(str(count + 1))

    return invoice_number

# -------- Form Fields --------
company = st.text_input("Sponsor Company Name")
contact = st.text_input("Contact Person")
email = st.text_input("Email")

# additional billing information
bill_to = st.text_area("Bill To (company / individual and address)")
from_info = st.text_area("From ", value="2187 Fellowship Rd, Tucker, GA 30084")

# financial breakdown
amount = st.number_input("Amount ($)", min_value=0.0)
discount = st.number_input("Discount ($)", min_value=0.0, value=0.0)
payment_method = st.selectbox("Payment Method", ["Credit Card", "Bank Transfer", "Check", "Cash", "Other"])

# Auto date
date_today = datetime.now().strftime("%B %d, %Y")
st.write("Invoice Date:", date_today)

invoice_no = generate_invoice_number()
st.write("Invoice Number:", invoice_no)

# -------- PDF Generator --------
def create_pdf():

    pdf = FPDF()
    # register custom Pacifico font for handwritten signature
    pdf.add_font("Pacifico", "", "Pacifico-Regular.ttf", uni=True)

    # tighter margins give more usable space
    pdf.set_margins(10, 10, 10)
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Text watermark
    pdf.set_font("Times", "B", 50)
    pdf.set_text_color(180, 180, 180)  # light gray
    # place watermark in the center, rotated slightly
    pdf.rotate(45, x=pdf.w/2, y=pdf.h/2)
    pdf.text(x=pdf.w/4, y=pdf.h/2, txt="MUNA Georgia")
    pdf.rotate(0)  # reset rotation
    pdf.set_text_color(0, 0, 0)  # restore color

    # Main Logo
    pdf.image("muna_logo.png", x=10, y=8, w=30)
    # barcode in top-right corner (not necessarily scannable)
    # decorative barcode placeholder (alternating bars)
    x = 150
    y = 8
    pattern = [1,2,1,2,1,2,1,2,1,2]
    for w in pattern:
        pdf.set_fill_color(0,0,0)
        pdf.rect(x, y, w, 10, 'F')
        x += w + 1

    # header text (slightly smaller)
    pdf.set_font("Times", "B", 14)
    pdf.cell(0,8,"MUNA Georgia", ln=True, align="C")

    pdf.set_font("Times", "", 12)
    pdf.cell(0,8,"Muslim Ummah of North America", ln=True, align="C")

    pdf.ln(4)

    pdf.set_font("Times","B",12)
    pdf.cell(0,8,"SPONSORSHIP INVOICE", ln=True, align="C")

    pdf.ln(6)

    pdf.set_font("Times","",11)

    pdf.cell(0,6,f"Invoice Number: {invoice_no}", ln=True)
    pdf.cell(0,6,f"Invoice Date: {date_today}", ln=True)

    pdf.ln(4)

    pdf.cell(0,6,f"Sponsor Company: {company}", ln=True)
    pdf.cell(0,6,f"Contact Person: {contact}", ln=True)
    pdf.cell(0,6,f"Email: {email}", ln=True)

    pdf.ln(6)

    # billing details
    # place bill-to and from information side by side
    col_width = (pdf.w - pdf.l_margin - pdf.r_margin - 10) / 2  # two columns with 10mm gap
    pdf.set_font("Times","B",12)
    pdf.cell(col_width,8,"Bill To:", border=0)
    pdf.cell(10,8,"")  # spacer
    pdf.cell(col_width,8,"From:", ln=True)
    pdf.set_font("Times","",12)
    bill_lines = bill_to.split("\n")
    from_lines = from_info.split("\n")
    max_lines = max(len(bill_lines), len(from_lines))
    for i in range(max_lines):
        bl = bill_lines[i] if i < len(bill_lines) else ""
        fl = from_lines[i] if i < len(from_lines) else ""
        pdf.cell(col_width,6,bl, border=0)
        pdf.cell(10,6,"")
        pdf.cell(col_width,6,fl, ln=True, border=0)

    pdf.ln(4)

    # financial table
    pdf.set_font("Times","B",11)
    pdf.cell(80,8,"Description", border=1)
    pdf.cell(25,8,"Amount ($)", border=1)
    pdf.cell(25,8,"Discount ($)", border=1)
    pdf.cell(40,8,"Payment Method", border=1, ln=True)

    pdf.set_font("Times","",11)
    pdf.cell(80,8,"Event Sponsorship Contribution", border=1)
    pdf.cell(25,8,f"{amount}", border=1)
    pdf.cell(25,8,f"{discount}", border=1)
    pdf.cell(40,8,f"{payment_method}", border=1, ln=True)

    pdf.ln(4)

    subtotal = amount
    total = amount - discount

    pdf.set_font("Times","B",11)
    pdf.cell(120,8,"Subtotal", border=1)
    pdf.cell(30,8,f"${subtotal:.2f}", border=1, ln=True)
    pdf.cell(120,8,"Discount", border=1)
    pdf.cell(30,8,f"-${discount:.2f}", border=1, ln=True)
    pdf.cell(120,8,"Total", border=1)
    pdf.cell(30,8,f"${total:.2f}", border=1, ln=True)

    pdf.set_font("Times","",10)
    pdf.multi_cell(0,6,
    "Thank you for supporting MUNA Georgia. Your sponsorship helps us serve the community and organize beneficial programs.")

    # immediately follow thank-you with signature block (compact)
    pdf.ln(2)
    pdf.set_font("Times","",11)
    
    
    pdf.set_font("Pacifico","",11)
    pdf.cell(0,4,"abdullah", ln=True, align="L")
    pdf.cell(0,8,"____________________________", ln=True)
    pdf.set_font("Times","",9)
    pdf.cell(0,4,"Abdullah Mamun", ln=True)
    pdf.cell(0,4,"President", ln=True)
    pdf.cell(0,4,"MUNA Georgia", ln=True)

    file_name = f"invoice_{invoice_no}.pdf"
    pdf.output(file_name)

    return file_name

# -------- Generate Button --------
if st.button("Generate Invoice PDF"):

    pdf_file = create_pdf()

    with open(pdf_file, "rb") as f:
        st.download_button(
            label="Download Invoice",
            data=f,
            file_name=pdf_file,
            mime="application/pdf"
        )
