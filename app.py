import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
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

# ---------------- POSITIVE UI + SHORT INPUTS ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #e0f7fa, #f1f8e9);
}
h1 {
    text-align: center;
    color: #00695c;
}
label {
    color: #00695c !important;
    font-weight: 600;
}
input, select {
    height: 35px !important;
    border-radius: 8px !important;
}
.stNumberInput input {
    height: 35px !important;
}
.stTextInput input {
    height: 35px !important;
}
.stSelectbox select {
    height: 35px !important;
}
.stButton>button {
    background: linear-gradient(to right, #26a69a, #66bb6a);
    color: white;
    font-size: 16px;
    border-radius: 10px;
    height: 42px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🎓 Student Marksheet Generator</h1>", unsafe_allow_html=True)

# ---------------- STUDENT DETAILS ----------------
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        school_name = st.text_input("School / College Name")
        student_name = st.text_input("Student Name")
        register_no = st.text_input("Register Number")
        father_name = st.text_input("Father Name")
    with col2:
        dob = st.date_input("Date of Birth")
        mother_name = st.text_input("Mother Name")
        attendance = st.number_input("Attendance %", 0, 100)
        photo = st.file_uploader("Student Photo", ["png", "jpg", "jpeg"])

# ---------------- PARENT DETAILS ----------------
st.subheader("👨‍👩‍👧 Parent Details")
p1, p2 = st.columns(2)
parent_mobile = p1.text_input("Parent Mobile")
parent_email = p2.text_input("Parent Email")

# ---------------- STUDENT TYPE ----------------
student_type = st.selectbox("Student Type", ["School Student", "College Student"])

# ---------------- SCHOOL MODULE ----------------
if student_type == "School Student":
    group = st.selectbox("Group", ["Biology", "Computer Science", "Commerce", "History"])
    school_subjects = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }
    subjects = school_subjects[group]

# ---------------- COLLEGE MODULE ----------------
if student_type == "College Student":
    department = st.selectbox("Department", ["CSE", "ECE", "Biotechnology"])
    semester = st.selectbox("Semester", [f"SEM {i}" for i in range(1, 9)])
    college_subjects = {
        "CSE": ["DS", "OS", "DBMS", "Python", "Java", "Networks"],
        "ECE": ["Signals", "Electronics", "Microprocessor", "Comm Systems", "Maths", "Physics"],
        "Biotechnology": ["Genetics", "Biochemistry", "Microbiology", "Cell Biology", "Chemistry", "Physics"]
    }
    subjects = college_subjects[department]

# ---------------- MARK INPUTS (COMPACT) ----------------
st.subheader("📘 Enter Marks")
marks = {}
cols = st.columns(3)
for i, sub in enumerate(subjects):
    marks[sub] = cols[i % 3].number_input(sub, 0, 100, key=sub)

# ---------------- GRADE LOGIC ----------------
def grade_calc(m):
    if m >= 90: return "A+", "Pass", colors.lightgreen
    elif m >= 75: return "A", "Pass", colors.lawngreen
    elif m >= 60: return "B", "Pass", colors.khaki
    elif m >= 50: return "C", "Pass", colors.lightyellow
    else: return "D", "Fail", colors.salmon

# ---------------- GENERATE ----------------
if st.button("📄 Generate Marksheet"):
    total = sum(marks.values())
    avg = total / len(marks)

    # ---------- TABLE IN APP ----------
    st.subheader("📊 Marksheet")
    table = [["Subject", "Marks", "Grade", "Result"]]
    for s, m in marks.items():
        g, r, _ = grade_calc(m)
        table.append([s, m, g, r])
    st.table(table)

    # ---------- PDF ----------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f"<font size=18 color='#00695c'><b>{school_name}</b></font>", styles["Title"]))
    elements.append(Spacer(1, 8))

    if photo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img:
            img.write(photo.getvalue())
            elements.append(Image(img.name, 80, 80))

    info = f"""
    <b>Name:</b> {student_name}<br/>
    <b>Register No:</b> {register_no}<br/>
    <b>DOB:</b> {dob}<br/>
    <b>Attendance:</b> {attendance}%
    """
    elements.append(Paragraph(info, styles["Normal"]))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>ANNUAL EXAMINATION RESULT</b>", styles["Heading2"]))
    elements.append(Spacer(1, 10))

    data = [["Subject", "Marks", "Grade", "Pass / Fail"]]
    row_colors = []
    for s, m in marks.items():
        g, r, c = grade_calc(m)
        data.append([s, str(m), g, r])
        row_colors.append(c)

    table_pdf = Table(data, colWidths=[140, 50, 50, 70])
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightblue),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey)
    ])
    for i, c in enumerate(row_colors, start=1):
        style.add("BACKGROUND", (0, i), (-1, i), c)

    table_pdf.setStyle(style)
    elements.append(table_pdf)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"<b>Total:</b> {total} &nbsp;&nbsp; <b>Average:</b> {avg:.2f}", styles["Normal"]))

    doc.build(elements)

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    st.success("✅ PDF Generated")
    st.download_button("⬇ Download PDF", pdf_bytes, f"{student_name}_marksheet.pdf", "application/pdf")
