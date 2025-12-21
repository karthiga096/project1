import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
import os
import base64

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Student Marksheet Portal",
    page_icon="🎓",
    layout="wide"
)

st.markdown("<h1 style='text-align:center;color:#00695c;'>🎓 Student Marksheet Generator</h1>", unsafe_allow_html=True)

# ---------------- STUDENT DETAILS (LINE-BY-LINE) ----------------
st.subheader("📘 Student Details")
school_name = st.text_input("School / College Name")
student_name = st.text_input("Student Name")
register_no = st.text_input("Register Number")
dob = st.date_input("Date of Birth")
father_name = st.text_input("Father Name")
mother_name = st.text_input("Mother Name")
attendance = st.number_input("Attendance %", 0, 100)
photo = st.file_uploader("Upload Student Photo", ["png", "jpg", "jpeg"])

# ---------------- PARENT DETAILS ----------------
st.subheader("👨‍👩‍👧 Parent Details")
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

# ---------------- COLLEGE MODULE ----------------
if student_type == "College Student":
    department = st.selectbox("Department", ["CSE","ECE","Biotechnology","AIDS","IT","AIML","EEE","Mechanical","Civil"])
    semester = st.selectbox("Semester", [f"SEM {i}" for i in range(1, 9)])
    college_subjects = {
        "CSE": ["DS", "OS", "DBMS", "Python", "Java", "Networks"],
        "ECE": ["Signals", "Electronics", "Microprocessor", "Comm Systems", "Maths", "Physics"],
        "Biotechnology": ["Genetics", "Biochemistry", "Microbiology", "Cell Biology", "Chemistry", "Physics"],
        "AIDS": ["AI Basics", "Data Science", "Python", "Statistics", "ML", "Python Project"],
        "IT": ["Networking", "Python", "Web Dev", "DBMS", "Linux", "Cyber Security"],
        "AIML": ["AI", "ML", "DL", "Python", "Data Analytics", "Project"],
        "EEE": ["Circuits", "Electronics", "Power Systems", "Control Systems", "Maths", "Physics"],
        "Mechanical": ["Thermodynamics", "Mechanics", "Machine Design", "CAD", "Materials", "Manufacturing"],
        "Civil": ["Surveying", "Concrete", "Structures", "Fluid Mechanics", "Construction", "Design"]
    }
    subjects = college_subjects[department]

# ---------------- MARK INPUTS (LINE-BY-LINE) ----------------
st.subheader("📘 Enter Marks")
marks = {}
for sub in subjects:
    marks[sub] = st.number_input(sub, 0, 100, key=sub)

# ---------------- GRADE LOGIC ----------------
def grade_calc(mark):
    if mark >= 90: return "A+", "Pass", colors.HexColor("#66ff66")  # Bright Green
    elif mark >= 75: return "A", "Pass", colors.HexColor("#99ff99")  # Light Green
    elif mark >= 60: return "B", "Pass", colors.HexColor("#ffff99")  # Yellow
    elif mark >= 50: return "C", "Pass", colors.HexColor("#ffcc99")  # Orange
    else: return "D", "Fail", colors.HexColor("#ff6666")            # Red

# ---------------- GENERATE MARKSHEET ----------------
if st.button("📄 Generate Marksheet"):
    total = sum(marks.values())
    avg = total / len(subjects)

    # ---------- TABLE IN APP ----------
    st.subheader("📊 Marksheet Preview")
    table_display = [["Subject","Marks","Grade","Result"]]
    for sub in subjects:
        g, r, _ = grade_calc(marks[sub])
        table_display.append([sub, marks[sub], g, r])
    st.table(table_display)

    # ---------- PDF GENERATION ----------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # School/College Name
    elements.append(Paragraph(f"<font size=18 color='#00695c'><b>{school_name}</b></font>", styles["Title"]))
    elements.append(Spacer(1,8))

    # Photo
    if photo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_tmp:
            img_tmp.write(photo.getvalue())
            elements.append(Image(img_tmp.name, width=80, height=80))

    # Student Info
    info_text = f"""
    <b>Name:</b> {student_name}<br/>
    <b>Register No:</b> {register_no}<br/>
    <b>DOB:</b> {dob}<br/>
    <b>Father:</b> {father_name}<br/>
    <b>Mother:</b> {mother_name}<br/>
    <b>Attendance:</b> {attendance}%
    """
    elements.append(Paragraph(info_text, styles["Normal"]))
    elements.append(Spacer(1,10))

    # Heading
    elements.append(Paragraph("<b>ANNUAL EXAMINATION RESULT</b>", styles["Heading2"]))
    elements.append(Spacer(1,10))

    # Table
    data = [["Subject","Marks","Grade","Pass / Fail"]]
    row_colors = []
    for sub in subjects:
        g, r, c = grade_calc(marks[sub])
        data.append([sub, str(marks[sub]), g, r])
        row_colors.append(c)

    table_pdf = Table(data, colWidths=[140,50,50,70])
    style = TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#4db6ac")), # Header teal
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#80cbc4"))
    ])
    for i, c in enumerate(row_colors, start=1):
        style.add("BACKGROUND",(0,i),(-1,i),c)
    table_pdf.setStyle(style)
    elements.append(table_pdf)

    # Totals
    elements.append(Spacer(1,10))
    elements.append(Paragraph(f"<b>Total:</b> {total} &nbsp;&nbsp; <b>Average:</b> {avg:.2f}", styles["Normal"]))

    doc.build(elements)

    # ---------- DOWNLOAD ----------
    with open(pdf_path,"rb") as f:
        pdf_bytes = f.read()
    st.success("✅ PDF Generated Successfully")
    st.download_button("⬇ Download PDF", pdf_bytes, f"{student_name}_marksheet.pdf", "application/pdf")
