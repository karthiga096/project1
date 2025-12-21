# ============================
# Student Marksheet Generator
# ============================

import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import tempfile
import os
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Student Marksheet Portal",
    page_icon="🎓",
    layout="wide"
)

# ---------------- UI STYLE ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #1f4037, #99f2c8);
}
h1 { text-align:center; color:#003366; }
.card {
    background-color:white;
    padding:15px;
    border-radius:15px;
    box-shadow:0px 4px 15px rgba(0,0,0,0.2);
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 Student Marksheet Generator</h1>", unsafe_allow_html=True)

# ---------------- STUDENT DETAILS ----------------
with st.expander("📘 Student Details", expanded=True):
    school_name = st.text_input("School / College Name")
    student_name = st.text_input("Student Name")
    register_no = st.text_input("Register Number")
    dob = st.date_input("Date of Birth")
    father_name = st.text_input("Father Name")
    mother_name = st.text_input("Mother Name")
    attendance = st.number_input("Attendance Percentage", 0, 100)
    photo = st.file_uploader("Upload Student Photo", ["png", "jpg", "jpeg"])

# ---------------- PARENT DETAILS ----------------
with st.expander("👨‍👩‍👧 Parent Details"):
    parent_mobile = st.text_input("Parent Mobile Number")
    parent_email = st.text_input("Parent Email")

# ---------------- STUDENT TYPE ----------------
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])

# ---------------- SCHOOL MODULE ----------------
if student_type == "School Student":
    group = st.selectbox("Select Group", ["Biology", "Computer Science", "Commerce", "History"])

    school_subjects = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }

    subjects = school_subjects[group]
    marks = {sub: st.number_input(f"{sub} Marks", 0, 100) for sub in subjects}

# ---------------- COLLEGE MODULE ----------------
if student_type == "College Student":
    department = st.selectbox("Select Department", ["CSE", "ECE", "Biotechnology"])
    semester = st.selectbox("Select Semester", [f"SEM {i}" for i in range(1, 9)])

    college_subjects = {
        "CSE": ["DS", "OS", "DBMS", "Python", "Java", "Networks"],
        "ECE": ["Signals", "Electronics", "Microprocessor", "Comm Systems", "Maths", "Physics"],
        "Biotechnology": ["Genetics", "Biochemistry", "Microbiology", "Cell Biology", "Chemistry", "Physics"]
    }

    subjects = college_subjects[department]
    marks = {sub: st.number_input(f"{sub} Marks", 0, 100) for sub in subjects}

# ---------------- GRADE LOGIC ----------------
def grade_calc(mark):
    if mark >= 90:
        return "A+", "Pass", colors.HexColor("#66FF66")
    elif mark >= 75:
        return "A", "Pass", colors.HexColor("#99FF99")
    elif mark >= 60:
        return "B", "Pass", colors.HexColor("#FFFF99")
    elif mark >= 50:
        return "C", "Pass", colors.HexColor("#FFCC99")
    else:
        return "D", "Fail", colors.HexColor("#FF6666")

# ---------------- GENERATE MARKSHEET ----------------
if st.button("📄 Generate Marksheet & PDF"):
    total = sum(marks.values())
    average = total / len(marks)

    # -------- DISPLAY IN APP --------
    display_table = [["Subject", "Marks", "Grade", "Result"]]
    for sub, mark in marks.items():
        g, res, _ = grade_calc(mark)
        display_table.append([sub, mark, g, res])

    st.subheader("📊 Marksheet Preview")
    st.table(display_table)

    # -------- PDF CREATION --------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # School Name
    elements.append(Paragraph(
        f"<font size=18 color='#003366'><b>{school_name}</b></font>",
        styles["Title"]
    ))
    elements.append(Spacer(1, 8))

    # Photo (Top Right)
    if photo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
            img_tmp.write(photo.getvalue())
            img_path = img_tmp.name
        img = Image(img_path, width=90, height=90)
        elements.append(img)

    # Student Info
    info = f"""
    <b>Name:</b> {student_name}<br/>
    <b>Register No:</b> {register_no}<br/>
    <b>DOB:</b> {dob}<br/>
    <b>Father:</b> {father_name}<br/>
    <b>Mother:</b> {mother_name}<br/>
    <b>Attendance:</b> {attendance}%
    """
    elements.append(Paragraph(info, styles["Normal"]))
    elements.append(Spacer(1, 10))

    # Heading
    elements.append(Paragraph(
        "<font size=14 color='#003366'><b>ANNUAL EXAMINATION RESULT</b></font>",
        styles["Heading2"]
    ))
    elements.append(Spacer(1, 10))

    # Table Data
    table_data = [["Subject", "Marks", "Grade", "Pass / Fail"]]
    row_colors = []

    for sub, mark in marks.items():
        g, res, color = grade_calc(mark)
        table_data.append([sub, str(mark), g, res])
        row_colors.append(color)

    table = Table(table_data, colWidths=[140, 50, 50, 70])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
    ])

    for i, clr in enumerate(row_colors, start=1):
        style.add("BACKGROUND", (0, i), (-1, i), clr)

    table.setStyle(style)
    elements.append(table)

    # Totals
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        f"<b>Total:</b> {total} &nbsp;&nbsp; <b>Average:</b> {average:.2f}",
        styles["Normal"]
    ))

    # Cutoffs
    if student_type == "School Student":
        if group in ["Biology", "Computer Science"]:
            eng_cutoff = marks.get("Maths", 0) + (marks.get("Physics", 0) + marks.get("Chemistry", 0)) / 2
            elements.append(Paragraph(f"<b>Engineering Cutoff:</b> {eng_cutoff}", styles["Normal"]))
        if group == "Biology":
            med_cutoff = marks["Biology"] + (marks["Physics"] + marks["Chemistry"]) / 2
            elements.append(Paragraph(f"<b>Medical Cutoff:</b> {med_cutoff}", styles["Normal"]))

    doc.build(elements)

    # -------- DOWNLOAD --------
    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    st.success("✅ Marksheet PDF Generated")
    st.download_button(
        "📥 Download Marksheet PDF",
        data=pdf_bytes,
        file_name=f"{student_name}_marksheet.pdf",
        mime="application/pdf"
    )

    # -------- SEND EMAIL --------
    if st.checkbox("📧 Send PDF to Parent Email"):
        api_key = os.getenv("SENDGRID_API_KEY")
        if not api_key:
            st.error("❌ SENDGRID_API_KEY not set in environment")
        else:
            encoded = base64.b64encode(pdf_bytes).decode()
            attachment = Attachment(
                FileContent(encoded),
                FileName("Marksheet.pdf"),
                FileType("application/pdf"),
                Disposition("attachment")
            )
            mail = Mail(
                from_email="verified_school_email@example.com",
                to_emails=parent_email,
                subject="Student Marksheet",
                html_content="Please find attached your child's marksheet."
            )
            mail.attachment = attachment
            sg = SendGridAPIClient(api_key)
            sg.send(mail)
            st.success("📨 Email sent successfully")
