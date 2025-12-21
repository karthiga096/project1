import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Official Student Marksheet", page_icon="🎓", layout="wide")
st.markdown("<h1 style='text-align:center;color:#00695c;'>🎓 Official Student Marksheet Generator</h1>", unsafe_allow_html=True)

# ---------------- STUDENT DETAILS ----------------
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
        "AIDS": ["AI Basics", "Data Science", "Python Programming", "Statistics", "ML Algorithms", "Project Work"],
        "IT": ["Networking", "Python", "Web Dev", "DBMS", "Linux", "Cyber Security"],
        "AIML": ["AI Fundamentals", "Machine Learning", "Deep Learning", "Python Programming", "Data Analytics", "Project Work"],
        "EEE": ["Circuits", "Electronics", "Power Systems", "Control Systems", "Electrical Machines", "Instrumentation"],
        "Mechanical": ["Thermodynamics", "Mechanics", "Machine Design", "CAD", "Materials Science", "Manufacturing Processes"],
        "Civil": ["Surveying", "Concrete Technology", "Structural Analysis", "Fluid Mechanics", "Construction Management", "Design Project"]
    }
    subjects = college_subjects[department]

# ---------------- ENTER MARKS ----------------
st.subheader("📘 Enter Marks")
marks = {}
for sub in subjects:
    marks[sub] = st.number_input(sub, 0, 100, key=sub)

# ---------------- GRADE LOGIC ----------------
def grade_calc(mark):
    if mark >= 90: return "A+", "Pass", colors.HexColor("#66ff66") # Bright Green
    elif mark >= 75: return "A", "Pass", colors.HexColor("#99ff99") # Light Green
    elif mark >= 60: return "B", "Pass", colors.HexColor("#ffff99") # Yellow
    elif mark >= 50: return "C", "Pass", colors.HexColor("#ffcc99") # Orange
    else: return "D", "Fail", colors.HexColor("#ff6666")           # Red

# ---------------- GENERATE MARKSHEET ----------------
if st.button("📄 Generate Official Marksheet"):
    total = sum(marks.values())
    avg = total / len(subjects)

    # ---------- STREAMLIT TABLE ----------
    st.subheader("📊 Marksheet Preview")
    table_display = [["Subject","Marks","Grade","Result"]]
    for sub in subjects:
        g,r,_ = grade_calc(marks[sub])
        table_display.append([sub, marks[sub], g, r])
    st.table(table_display)

    # ---------- PDF GENERATION ----------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf_path = tmp.name

    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    # ---------- HEADER ----------
    elements.append(Paragraph(f"<font size=18 color='#00695c'><b>{school_name}</b></font>", styles["Title"]))
    elements.append(Spacer(1,6))
    elements.append(Paragraph("<b>Annual Examination Marksheet</b>", styles["Heading2"]))
    elements.append(Spacer(1,10))

    # Photo Top-Right
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

    # ---------- TABLE ----------
    data = [["Subject","Marks","Grade","Pass/Fail"]]
    row_colors = []
    for sub in subjects:
        g,r,c = grade_calc(marks[sub])
        data.append([sub, str(marks[sub]), g, r])
        row_colors.append(c)

    table = Table(data, colWidths=[140,50,50,70])
    style = TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#4db6ac")), # Teal header
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER"),
        ("GRID",(0,0),(-1,-1),0.8,colors.HexColor("#80cbc4")),
        ("BOX",(0,0),(-1,-1),1,colors.HexColor("#4db6ac"))
    ])
    for i,color in enumerate(row_colors,start=1):
        style.add("BACKGROUND",(0,i),(-1,i),color)
    table.setStyle(style)
    elements.append(table)

    # Totals
    elements.append(Spacer(1,10))
    elements.append(Paragraph(f"<b>Total:</b> {total} &nbsp;&nbsp; <b>Average:</b> {avg:.2f}", styles["Normal"]))
    elements.append(Spacer(1,10))

    # Legend
    legend_data = [
        ["Legend","Color Meaning"],
        ["A+/A","Excellent"],
        ["B","Good"],
        ["C","Average"],
        ["D","Fail"]
    ]
    legend_colors = [colors.lightgrey, colors.HexColor("#66ff66"), colors.HexColor("#ffff99"), colors.HexColor("#ffcc99"), colors.HexColor("#ff6666")]
    legend_table = Table(legend_data, colWidths=[80,150])
    legend_style = TableStyle([
        ("GRID",(0,0),(-1,-1),0.5,colors.HexColor("#80cbc4")),
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#4db6ac")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("ALIGN",(0,0),(-1,-1),"CENTER")
    ])
    for i,color in enumerate(legend_colors,start=1):
        legend_style.add("BACKGROUND",(0,i),(-1,i),color)
    legend_table.setStyle(legend_style)
    elements.append(legend_table)

    doc.build(elements)

    # ---------- DOWNLOAD ----------
    with open(pdf_path,"rb") as f:
        pdf_bytes = f.read()
    st.success("✅ Official PDF Marksheet Generated")
    st.download_button("⬇ Download PDF", pdf_bytes, f"{student_name}_marksheet.pdf", "application/pdf")
