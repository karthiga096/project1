import streamlit as st
import numpy as np
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import tempfile
import smtplib
from email.message import EmailMessage

# ---------------- GRADE FUNCTION ----------------
def grade(mark):
    if mark >= 90:
        return "A+", "Pass"
    elif mark >= 80:
        return "A", "Pass"
    elif mark >= 70:
        return "B+", "Pass"
    elif mark >= 60:
        return "B", "Pass"
    elif mark >= 50:
        return "C", "Pass"
    else:
        return "D", "Fail"

# ---------------- ML SUGGESTION ----------------
def lr_suggestion(marks):
    X = np.array(range(1, 7)).reshape(-1, 1)
    y = np.array(marks)
    model = LinearRegression()
    model.fit(X, y)
    return "Performance Improving" if model.coef_[0] > 0 else "Needs More Practice"

# ---------------- EMAIL FUNCTION ----------------
def send_email(sender_email, sender_password, receiver_email, pdf_path):
    try:
        msg = EmailMessage()
        msg["Subject"] = "Student Marksheet"
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg.set_content(
            "Dear Parent,\n\nPlease find the attached student marksheet.\n\nRegards,\nCollege"
        )

        with open(pdf_path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="pdf",
                filename="Marksheet.pdf"
            )

        # Outlook SMTP server (no app password needed)
        with smtplib.SMTP_SSL("smtp.office365.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)

        return True

    except Exception as e:
        st.warning(f"⚠️ Email could not be sent: {e}")
        return False

# ---------------- PDF GENERATION ----------------
def generate_pdf(name, roll, subjects, marks):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "COLLEGE MARKSHEET", ln=True, align="C")
    pdf.ln(8)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Student Name : {name}", ln=True)
    pdf.cell(0, 8, f"Roll Number  : {roll}", ln=True)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 10, "Subject", 1)
    pdf.cell(25, 10, "Marks", 1)
    pdf.cell(25, 10, "Grade", 1)
    pdf.cell(30, 10, "Result", 1)
    pdf.cell(70, 10, "Suggestion", 1)
    pdf.ln()

    suggestion = lr_suggestion(marks)
    for i in range(6):
        g, r = grade(marks[i])
        pdf.set_font("Arial", "", 11)
        pdf.cell(40, 10, subjects[i], 1)
        pdf.cell(25, 10, str(marks[i]), 1)
        pdf.cell(25, 10, g, 1)
        pdf.cell(30, 10, r, 1)
        pdf.cell(70, 10, suggestion, 1)
        pdf.ln()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    return temp.name

# ---------------- STREAMLIT UI ----------------
st.title("🎓 Smart Marksheet Generation using ML")

# Student info
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")

# Parent contact info
parent_email = st.text_input("Parent Email")
parent_mobile = st.text_input("Parent Mobile Number (Optional for display)")

# Sender credentials (Outlook)
st.subheader("Email Credentials for sending marksheet")
sender_email = st.text_input("Your Outlook Email (Sender)", "")
sender_password = st.text_input("Outlook Password", type="password")

# Subject marks
st.subheader("Enter Subject Marks")
subjects = ["Maths", "Science", "English", "History", "Computer", "Physics"]
marks = [st.number_input(sub, min_value=0, max_value=100) for sub in subjects]

# Generate button
if st.button("Generate Marksheet"):
    if name and roll and parent_email and sender_email and sender_password:
        pdf_path = generate_pdf(name, roll, subjects, marks)

        # Send Email
        email_status = send_email(sender_email, sender_password, parent_email, pdf_path)

        st.success("✅ Marksheet Generated Successfully")

        # Show download button
        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download Marksheet PDF",
                f,
                file_name=f"{roll}_Marksheet.pdf",
                mime="application/pdf"
            )

        # Display email & optional mobile info
        if email_status:
            st.info(f"📧 Email sent to: {parent_email}")
        if parent_mobile:
            st.info(f"📱 Parent Mobile: {parent_mobile}")

    else:
        st.error("❌ Please fill all required fields including Outlook credentials")
