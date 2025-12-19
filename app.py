import streamlit as st
import numpy as np
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import tempfile
import smtplib
from email.message import EmailMessage
from twilio.rest import Client

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

    if model.coef_[0] > 0:
        return "Performance Improving"
    else:
        return "Needs More Practice"

# ---------------- EMAIL FUNCTION ----------------
def send_email(receiver_email, pdf_path):
    sender_email = "yourgmail@gmail.com"
    sender_password = "your_app_password"  # Gmail App Password

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

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)

# ---------------- WHATSAPP FUNCTION ----------------
def send_whatsapp(mobile):
    account_sid = "YOUR_TWILIO_SID"
    auth_token = "YOUR_TWILIO_AUTH_TOKEN"

    client = Client(account_sid, auth_token)

    client.messages.create(
        from_="whatsapp:+14155238886",  # Twilio sandbox
        to=f"whatsapp:+91{mobile}",
        body="Your child’s marksheet has been generated and sent to your email."
    )

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

name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
parent_mobile = st.text_input("Parent WhatsApp Number")
parent_email = st.text_input("Parent Email")

st.subheader("Enter Subject Marks")

subjects = ["Maths", "Science", "English", "History", "Computer", "Physics"]
marks = [st.number_input(sub, min_value=0, max_value=100) for sub in subjects]

if st.button("Generate Marksheet"):
    if name and roll and parent_mobile and parent_email:
        pdf_path = generate_pdf(name, roll, subjects, marks)

        send_email(parent_email, pdf_path)
        send_whatsapp(parent_mobile)

        st.success("✅ Marksheet Generated & Sent Successfully")

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download Marksheet PDF",
                f,
                file_name=f"{roll}_Marksheet.pdf",
                mime="application/pdf"
            )

        st.info(f"📧 Email sent to: {parent_email}")
        st.info(f"📱 WhatsApp message sent to: {parent_mobile}")

    else:
        st.error("❌ Please fill all fields")

