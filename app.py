import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Student Mark Portal",
    page_icon="🎓",
    layout="centered"
)

# ----------------- CUSTOM CSS -----------------
st.markdown("""
<style>
/* Background Gradient */
.stApp {
    background: linear-gradient(to right, #667eea, #764ba2);
    font-family: 'Segoe UI', sans-serif;
}

/* Title */
.main-title {
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 10px;
}

/* Subtitle */
.sub-title {
    text-align: center;
    color: #f1f1f1;
    font-size: 18px;
    margin-bottom: 30px;
}

/* Card */
.card {
    background-color: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 25px;
}

/* Result Box */
.result {
    background: linear-gradient(to right, #43cea2, #185a9d);
    padding: 20px;
    border-radius: 15px;
    color: white;
    font-size: 18px;
    text-align: center;
    margin-top: 20px;
}

/* Button */
.stButton>button {
    background: linear-gradient(to right, #ff512f, #dd2476);
    color: white;
    font-size: 18px;
    border-radius: 12px;
    height: 50px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ----------------- PAGE HEADER -----------------
st.markdown("<div class='main-title'>🎓 Student Mark Generation Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Smart | Colourful | Easy to Use</div>", unsafe_allow_html=True)

# ----------------- STUDENT DETAILS -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
college = st.text_input("🏫 School / College Name")
student_type = st.selectbox("🎒 Student Type", ["School Student", "College Student"])
name = st.text_input("👨‍🎓 Student Name")
roll = st.text_input("🆔 Roll Number")
attendance = st.number_input("📊 Attendance Percentage", 0, 100)
photo = st.file_uploader("🖼 Upload Student Photo", type=["png", "jpg", "jpeg"])
st.markdown("</div>", unsafe_allow_html=True)

# Display photo preview
if photo:
    st.image(photo, width=180, caption="Student Photo")

# ----------------- SUBJECT MARKS -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Subject Marks")
m1 = st.slider("Mathematics", 0, 100)
m2 = st.slider("Science", 0, 100)
m3 = st.slider("English", 0, 100)
m4 = st.slider("Computer Science", 0, 100)
m5 = st.slider("Social Science", 0, 100)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- RESULT CALCULATION -----------------
if st.button("✨ Generate Result"):
    total = m1 + m2 + m3 + m4 + m5
    avg = total / 5

    if avg >= 90:
        grade = "A+"
    elif avg >= 75:
        grade = "A"
    elif avg >= 60:
        grade = "B"
    elif avg >= 50:
        grade = "C"
    else:
        grade = "Fail"

    # Display result
    st.markdown(f"""
<div class='result'>
🎯 <b>Total Marks:</b> {total} / 500 <br>
📈 <b>Average:</b> {avg:.2f}% <br>
🏆 <b>Grade:</b> {grade} <br>
📊 <b>Attendance:</b> {attendance}%
</div>
""", unsafe_allow_html=True)

    # ----------------- PDF GENERATION -----------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"{college}", ln=True, align="C")
    pdf.cell(0, 10, f"Student Marksheet", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Roll No: {roll}", ln=True)
    pdf.cell(0, 10, f"Student Type: {student_type}", ln=True)
    pdf.cell(0, 10, f"Attendance: {attendance}%", ln=True)
    pdf.ln(5)
    
    pdf.cell(0, 10, f"Mathematics: {m1}", ln=True)
    pdf.cell(0, 10, f"Science: {m2}", ln=True)
    pdf.cell(0, 10, f"English: {m3}", ln=True)
    pdf.cell(0, 10, f"Computer Science: {m4}", ln=True)
    pdf.cell(0, 10, f"Social Science: {m5}", ln=True)
    pdf.ln(5)
    
    pdf.cell(0, 10, f"Total Marks: {total}/500", ln=True)
    pdf.cell(0, 10, f"Average: {avg:.2f}%", ln=True)
    pdf.cell(0, 10, f"Grade: {grade}", ln=True)

    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        pdf.output(tmp_file.name)
        st.success("✅ PDF Generated Successfully!")
        st.download_button(
            label="📥 Download Marksheet PDF",
            data=open(tmp_file.name, "rb").read(),
            file_name=f"{name}_marksheet.pdf",
            mime="application/pdf"
        )

# ----------------- OPTIONAL: Email PDF -----------------
# You can uncomment and configure this section to send the PDF via email
"""
import smtplib
from email.message import EmailMessage

sender_email = "your_email@example.com"
sender_password = "your_password"
receiver_email = "parent_email@example.com"

msg = EmailMessage()
msg["Subject"] = "Student Marksheet"
msg["From"] = sender_email
msg["To"] = receiver_email
msg.set_content("Please find the marksheet attached.")

with open(tmp_file.name, "rb") as f:
    file_data = f.read()
    msg.add_attachment(file_data, maintype="application", subtype="pdf", filename=f"{name}_marksheet.pdf")

with smtplib.SMTP_SSL("smtp.example.com", 465) as server:
    server.login(sender_email, sender_password)
    server.send_message(msg)
    st.success("📧 Email sent successfully!")
"""
