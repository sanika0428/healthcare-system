import streamlit as st
import pandas as pd
from datetime import datetime
import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


def generate_bill_pdf(bill):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Hospital Billing Receipt</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    elements.append(Paragraph(f"Patient Name: {bill['Patient Name']}", styles["Normal"]))
    elements.append(Paragraph(f"Disease: {bill['Disease']}", styles["Normal"]))
    elements.append(Paragraph(f"Date: {bill['Date']}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    table_data = [
        ["Description", "Amount (₹)"],
        ["Consultation", bill["Consultation"]],
        ["Blood Test", bill["Blood Test"]],
        ["Urine Test", bill["Urine Test"]],
        ["Medicine", bill["Medicine"]],
        ["Hospital Stay", bill["Hospital Stay"]],
        ["GST (5%)", bill["GST"]],
        ["Total Amount", bill["Total Amount"]],
    ]

    table = Table(table_data, colWidths=[300, 150])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    doc.build(elements)

    buffer.seek(0)
    return buffer


def show_billing():
    st.title("💳 Patient Billing System")

    # ------------------ Patient Data ------------------
    patients = pd.DataFrame({
        "Patient ID": [101, 102, 103],
        "Name": ["Rahul Sharma", "Anita Verma", "Amit Singh"],
        "Disease": ["Flu", "Allergy", "Diabetes"]
    })

    # ------------------ Select Patient ------------------
    patient_id = st.selectbox("Select Patient ID", patients["Patient ID"])
    patient = patients[patients["Patient ID"] == patient_id].iloc[0]

    st.info(f"👤 Name: {patient['Name']} | 🦠 Disease: {patient['Disease']}")

    # ------------------ Fixed Consultation ------------------
    consultation = 500
    st.write("🩺 **Consultation Fee:** ₹500 (Fixed)")

    # ------------------ Tests ------------------
    st.subheader("🧪 Diagnostic Tests")

    blood_test = st.checkbox("Blood Test (₹500)")
    urine_test = st.checkbox("Urine Test (₹500)")

    blood_charge = 500 if blood_test else 0
    urine_charge = 500 if urine_test else 0

    # ------------------ Medicine ------------------
    medicine = st.number_input(
        "💊 Medicine Charges (₹)", min_value=0, max_value=15000, value=0
    )

    # ------------------ Hospital Stay ------------------
    days = st.number_input(
        "🏥 Hospital Stay (Days)", min_value=0, max_value=30, value=0
    )
    stay_cost = days * 1500

    # ------------------ Bill Calculation ------------------
    subtotal = (
        consultation +
        blood_charge +
        urine_charge +
        medicine +
        stay_cost
    )

    gst = subtotal * 0.05
    total = subtotal + gst

    # ------------------ Summary ------------------
    st.subheader("🧾 Bill Summary")
    st.write(f"Consultation: ₹{consultation}")
    st.write(f"Blood Test: ₹{blood_charge}")
    st.write(f"Urine Test: ₹{urine_charge}")
    st.write(f"Medicine: ₹{medicine}")
    st.write(f"Hospital Stay: ₹{stay_cost}")
    st.write(f"Subtotal: ₹{subtotal}")
    st.write(f"GST (5%): ₹{gst:.2f}")
    st.success(f"💰 Total Amount: ₹{total:.2f}")

    # ------------------ Generate Bill ------------------
    if st.button("Generate Bill"):
        st.session_state.bill = {
            "Patient Name": patient["Name"],
            "Disease": patient["Disease"],
            "Date": datetime.now().strftime("%d-%m-%Y"),
            "Consultation": consultation,
            "Blood Test": blood_charge,
            "Urine Test": urine_charge,
            "Medicine": medicine,
            "Hospital Stay": stay_cost,
            "GST": round(gst, 2),
            "Total Amount": round(total, 2)
        }

    # ------------------ Display & Download ------------------
    if "bill" in st.session_state:
        st.subheader("✅ Generated Bill")
        st.json(st.session_state.bill)

        pdf_file = generate_bill_pdf(st.session_state.bill)

        st.download_button(
            "⬇️ Download Bill as PDF",
            data=pdf_file,
            file_name=f"Bill_{st.session_state.bill['Patient Name']}.pdf",
            mime="application/pdf"
        )
