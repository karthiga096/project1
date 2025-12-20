# app.py
import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Student Mark Generation Portal",
    page_icon="🎓",
    layout="wide"
)

# -------------------- CUSTOM CSS --------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #667eea, #764ba2);
    font-family: 'Segoe UI', sans-serif;
}
.main-title {
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 10px;
}
.sub-title {
    text-align: center;
    color: #f1f1f1;
    font-size: 18px;
    margin-bottom: 30px;
}
.card {
    background-color: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 25px;
}
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

# -------------------- HEADER --------------------
st.markdown("<div class='main-title'>🎓 Student Mark Generation Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Dynamic Marksheet Generator for School and College Students</div>", unsafe_allow_html=True)

# -------------------- COMMON INPUTS --------------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", 0, 100)
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")
photo = st.file_uploader("Upload Student Photo", type=["png", "jpg", "jpeg"])
st.markdown("</div>", unsafe_allow_html=True)

if photo:
    st.image(photo, width=180, caption="Student Photo")

# -------------------- SCHOOL STUDENT MODULE --------------------
if student_type == "School Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    group = st.selectbox("Select Group", ["Biology", "Computer Science", "Commerce", "History / Arts"])

    # Subjects based on group
    subjects_dict = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }
    subjects = subjects_dict[group]

    marks = {}
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100, step=1)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- COLLEGE STUDENT MODULE --------------------
if student_type == "College Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    department = st.selectbox("Select Department", ["CSE", "ECE", "Biotechnology"])
    semester = st.selectbox("Select Semester", [f"Semester {i}" for i in range(1, 9)])

    # Subjects based on department and semester (example)
    college_subjects = {
        "CSE": ["DS", "OS", "DBMS", "Python", "Java", "Networking"],
        "ECE": ["Signals", "Electronics", "Microprocessor", "Communications", "Mathematics", "Physics"],
        "Biotechnology": ["Genetics", "Biochemistry", "Microbiology", "Cell Biology", "Chemistry", "Physics"]
    }
    subjects = college_subjects[department]

    marks = {}
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100, step=1)
    st.markdown("</div>", unsafe_allow_html=True)

# -------------------- GRADE & SUGGESTION LOGIC --------------------
def grade_calc(mark):
    if mark >= 90:
        return "A+", "Excellent", (0, 128, 0)
    elif mark >= 80:
        return "A", "Very Good", (34, 139, 34)
    elif mark >= 70:
        return "B+", "Good", (173, 255, 47)
    elif mark >= 60:
        return "B", "Average", (255, 255, 0)
    elif mark >= 50:
        return "C", "Below Average", (255, 165, 0)
    else:
        return "D / Fail", "Needs Improvement", (255, 0, 0)

# -------------------- GENERATE MARKSHEET --------------------
if st.button("Generate Marksheet & PDF"):
    total = sum(marks.values())
    avg = total / len(subjects)

    # -------------------- DISPLAY TABLE IN APP --------------------
    st.subheader("Marks Table")
    table_data = []
    for sub, mark in marks.items():
        g, suggestion, _ = grade_calc(mark)
        table_data.append([sub, mark, g, suggestion])
    st.table(table_data)

    # -------------------- PDF GENERATION --------------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Student Marksheet", ln=True, align="C")
    pdf.ln(5)

    # Student info
    pdf.set_font("Arial", "", 12)
    pdf.cell(50, 10, f"Name: {name}", border=1)
    pdf.cell(50, 10, f"Roll No: {roll}", border=1)
    pdf.cell(50, 10, f"Type: {student_type}", border=1)
    pdf.cell(0, 10, f"Attendance: {attendance}%", border=1, ln=True)
    pdf.ln(5)

    # Photo
    if photo:
        image = Image.open(photo)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(tmp_file.name)
        pdf.image(tmp_file.name, x=150, y=30, w=40)

    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Subject", border=1, align="C")
    pdf.cell(30, 10, "Marks", border=1, align="C")
    pdf.cell(30, 10, "Grade", border=1, align="C")
    pdf.cell(50, 10, "Suggestion", border=1, align="C")
    pdf.ln()

    # Table rows with color
    pdf.set_font("Arial", "", 12)
    for sub, mark in marks.items():
        g, suggestion, color = grade_calc(mark)
        pdf.set_fill_color(*color)
        pdf.cell(80, 10, sub, border=1)
        pdf.cell(30, 10, str(mark), border=1)
        pdf.cell(30, 10, g, border=1)
        pdf.cell(50, 10, suggestion, border=1, ln=True, fill=True)

    # Totals
    pdf.ln(5)
    pdf.cell(80, 10, "Total", border=1)
    pdf.cell(30, 10, str(total), border=1)
    pdf.cell(30, 10, "", border=1)
    pdf.cell(50, 10, "", border=1, ln=True)

    pdf.cell(80, 10, "Average", border=1)
    pdf.cell(30, 10, f"{avg:.2f}", border=1)
    pdf.cell(30, 10, "", border=1)
    pdf.cell(50, 10, "", border=1, ln=True)

    # School cutoff for school students
    if student_type == "School Student":
        if group == "Biology":
            med_cutoff = marks["Biology"] + (marks["Physics"] + marks["Chemistry"])/2
            pdf.ln(5)
            pdf.cell(0, 10, f"Medical Cutoff: {med_cutoff}", ln=True)
        eng_cutoff = marks.get("Maths",0) + (marks.get("Physics",0)+marks.get("Chemistry",0))/2
        pdf.cell(0, 10, f"Engineering Cutoff: {eng_cutoff}", ln=True)

    # Save PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        st.success("✅ PDF Generated Successfully!")
        st.download_button(
            label="📥 Download Marksheet PDF",
            data=open(tmp_pdf.name, "rb").read(),
            file_name=f"{name}_marksheet.pdf",
            mime="application/pdf"
        )
