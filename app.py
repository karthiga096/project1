import streamlit as st
from fpdf import FPDF
import pandas as pd
from PIL import Image

# ----------------- Page Config -----------------
st.set_page_config(page_title="Student Marksheet Portal", layout="wide")

# ----------------- Custom CSS -----------------
st.markdown("""
<style>
/* Page & Sidebar */
.stApp {background-color: #FFF8DC; color: black;}  /* Soft cream background */
[data-testid="stSidebar"] {background-color: #FFDAB9;} /* Light peach sidebar */

/* Headings */
h1, h2, h3, h4, h5, h6 {color: #8B4513; font-weight: bold; font-size: 28px;}

/* Labels & Inputs */
label, .stMarkdown p, .stTextInput label, .stNumberInput label {color: #8B4513 !important; font-weight: bold; font-size: 18px;}
.stTextInput>div>div>input,
.stNumberInput>div>div>input,
.stSelectbox>div>div>select,
.stFileUploader>div>div>input {
    color: black !important; 
    background-color: #FFF !important; 
    border: 2px solid #8B4513 !important; 
    border-radius: 8px;
    padding: 10px;
    font-size: 18px;
}

/* Buttons */
.stButton>button {background-color: #FF8C00; color: white; font-weight: bold; border-radius: 10px; padding: 12px 25px; font-size: 20px;}
.stButton>button:hover {background-color: #FF7F50;}

/* Table background */
.css-1d391kg {background-color: #FFF !important; font-size: 18px;} 
</style>
""", unsafe_allow_html=True)

st.title("🎓 Student Marksheet Portal")

st.markdown("### Step 1: Enter Student Details")
college_name = st.text_input("🏫 College/School Name", "KAMARAJ COLLEGE OF ENGINEERING AND TECHNOLOGY")
student_type = st.selectbox("👤 Select Student Type", ["School Student", "College Student"])
name = st.text_input("📝 Student Name")
roll = st.text_input("🆔 Roll Number")
attendance = st.number_input("📊 Attendance Percentage", 0, 100, 90)
parent_mobile = st.text_input("📱 Parent Mobile Number")
parent_email = st.text_input("✉ Parent Email")
photo_file = st.file_uploader("📷 Upload Student Photo", type=["png", "jpg", "jpeg"])

# ----------------- Helper Functions -----------------
def grade(mark):
    if mark >= 90: return "A+"
    elif mark >= 80: return "A"
    elif mark >= 70: return "B+"
    elif mark >= 60: return "B"
    elif mark >= 50: return "C"
    elif mark >= 35: return "D"
    else: return "F"

def pass_fail(mark):
    return "Pass" if mark >= 35 else "Fail"

def suggestion(mark):
    if mark >= 75: return "Excellent ✅"
    elif mark >= 50: return "Average ⚠️"
    else: return "Poor ❌"

# ----------------- School Groups -----------------
school_groups = {
    "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
    "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
    "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
    "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"],
    "Fine Arts": ["Tamil", "English", "Drawing", "Music", "History", "Geography"]
}

# ----------------- College Departments (Sem 1–8) -----------------
college_departments = {
    "CSE": {
        "Semester 1": ["Maths 1", "Physics 1", "Programming 1", "Electronics", "English", "Lab 1"],
        "Semester 2": ["Maths 2", "Data Structures", "Physics 2", "DBMS", "English", "Lab 2"],
        "Semester 3": ["Maths 3", "OOP", "Digital Logic", "Networks", "English", "Lab 3"],
        "Semester 4": ["Algorithms", "OS", "Database", "Software Eng", "English", "Lab 4"],
        "Semester 5": ["AI", "ML", "Cloud Computing", "Web Dev", "English", "Lab 5"],
        "Semester 6": ["Cybersecurity", "Big Data", "Embedded Systems", "Project 1", "English", "Lab 6"],
        "Semester 7": ["Mobile Dev", "IoT", "Project 2", "Entrepreneurship", "English", "Lab 7"],
        "Semester 8": ["Capstone Project", "Internship", "Ethics", "English", "Lab 8", "Elective"]
    },
    "ECE": {
        "Semester 1": ["Maths 1", "Physics 1", "Circuits 1", "Electronics 1", "English", "Lab 1"],
        "Semester 2": ["Maths 2", "Signals", "Electronics 2", "Communication", "English", "Lab 2"],
        "Semester 3": ["Digital Logic", "Microprocessors", "Networks", "Control Systems", "English", "Lab 3"],
        "Semester 4": ["VLSI", "Embedded Systems", "Electromagnetics", "Software Eng", "English", "Lab 4"],
        "Semester 5": ["AI Circuits", "Signal Processing", "Communication 2", "Project 1", "English", "Lab 5"],
        "Semester 6": ["IoT", "Networking 2", "Cybersecurity", "Project 2", "English", "Lab 6"],
        "Semester 7": ["Mobile Comm", "VLSI 2", "Project 3", "Entrepreneurship", "English", "Lab 7"],
        "Semester 8": ["Capstone Project", "Internship", "Ethics", "English", "Lab 8", "Elective"]
    },
    "Biotechnology": {
        "Semester 1": ["Biology 1", "Chemistry 1", "Maths 1", "Physics 1", "English", "Lab 1"],
        "Semester 2": ["Genetics", "Microbiology", "Chemistry 2", "Maths 2", "English", "Lab 2"],
        "Semester 3": ["Biochemistry", "Immunology", "Cell Biology", "English", "Lab 3", "Elective 1"],
        "Semester 4": ["Genomics", "Molecular Biology", "Bioinformatics", "English", "Lab 4", "Elective 2"],
        "Semester 5": ["Bioprocess", "Pharmacology", "Microbial Tech", "English", "Lab 5", "Elective 3"],
        "Semester 6": ["Genetic Engineering", "Plant Biotechnology", "Animal Biotechnology", "English", "Lab 6", "Elective 4"],
        "Semester 7": ["Industrial Biotech", "Research Methods", "Project 1", "English", "Lab 7", "Elective 5"],
        "Semester 8": ["Capstone Project", "Internship", "Ethics", "English", "Lab 8", "Elective 6"]
    },
    "Mechanical": {
        "Semester 1": ["Maths 1", "Physics 1", "Engineering Mechanics", "Drawing", "English", "Lab 1"],
        "Semester 2": ["Maths 2", "Thermodynamics 1", "Material Science", "Drawing 2", "English", "Lab 2"],
        "Semester 3": ["Fluid Mechanics", "Thermodynamics 2", "Manufacturing", "English", "Lab 3", "Elective 1"],
        "Semester 4": ["Dynamics", "Machine Design", "CAD", "English", "Lab 4", "Elective 2"],
        "Semester 5": ["Mechatronics", "Heat Transfer", "Vibrations", "English", "Lab 5", "Elective 3"],
        "Semester 6": ["Automobile Eng", "Robotics", "Project 1", "English", "Lab 6", "Elective 4"],
        "Semester 7": ["Industrial Eng", "Project 2", "Entrepreneurship", "English", "Lab 7", "Elective 5"],
        "Semester 8": ["Capstone Project", "Internship", "Ethics", "English", "Lab 8", "Elective 6"]
    }
}

marks = {}

# ----------------- Input for Subjects -----------------
st.markdown("### Step 2: Enter Subject Marks")
if student_type == "School Student":
    group = st.selectbox("📂 Select Group", list(school_groups.keys()))
    subjects = school_groups[group]
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100, 0)

    total = sum(marks.values())
    average = total / len(subjects)
    maths = marks.get("Maths",0)
    physics = marks.get("Physics",0)
    chemistry = marks.get("Chemistry",0)
    biology = marks.get("Biology",0)
    engineering_cutoff = maths + (physics + chemistry)/2
    medical_cutoff = biology + (physics + chemistry)/2 if "Biology" in subjects else "N/A"

elif student_type == "College Student":
    dept = st.selectbox("📂 Select Department", list(college_departments.keys()))
    sem = st.selectbox("📘 Select Semester", list(college_departments[dept].keys()))
    subjects = college_departments[dept][sem]
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100, 0)

# ----------------- Generate Marksheet -----------------
if st.button("✅ Generate Marksheet"):
    st.subheader("📝 Marksheet Preview")
    data = []
    for sub, mark in marks.items():
        data.append({"Subject": sub, "Marks": mark, "Grade": grade(mark),
                     "Result": pass_fail(mark), "Suggestion": suggestion(mark)})
    df = pd.DataFrame(data)
    st.dataframe(df)

    if student_type == "School Student":
        st.markdown(f"**Total Marks:** {total}")
        st.markdown(f"**Average Marks:** {average:.2f}")
        st.markdown(f"**Engineering Cutoff:** {engineering_cutoff}")
        if medical_cutoff != "N/A":
            st.markdown(f"**Medical Cutoff:** {medical_cutoff}")

    # ----------------- PDF Generation -----------------
    pdf = FPDF()
    pdf.add_page()
    pdf.set_fill_color(255, 250, 240)  # Cream background
    pdf.rect(0, 0, 210, 297, 'F')
    pdf.set_font("Arial", 'B', 18)
    pdf.set_text_color(75, 0, 130)  # Indigo

    pdf.set_y(10)
    pdf.cell(0, 12, college_name, ln=True, align="C")
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 12, "Student Marksheet", ln=True, align="C")
    pdf.ln(15)

    # Student Photo
    if photo_file is not None:
        image = Image.open(photo_file)
        image_path = "temp_photo.png"
        image.save(image_path)
        pdf.image(image_path, x=160, y=25, w=35, h=35)

    # Student details
    pdf.set_font("Arial", '', 14)
    pdf.set_text_color(0,0,0)
    pdf.cell(0, 10, f"Name: {name}", ln=True)
    pdf.cell(0, 10, f"Roll Number: {roll}", ln=True)
    pdf.cell(0, 10, f"Attendance: {attendance}%", ln=True)
    pdf.cell(0, 10, f"Parent Email: {parent_email}", ln=True)
    pdf.cell(0, 10, f"Parent Mobile: {parent_mobile}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(75, 0, 130)  # Indigo header
    pdf.set_text_color(255,255,255)
    pdf.set_draw_color(0,0,0)
    pdf.set_line_width(0.3)
    pdf.cell(50, 12, "Subject", 1, 0, 'C', fill=True)
    pdf.cell(25, 12, "Marks", 1, 0, 'C', fill=True)
    pdf.cell(25, 12, "Grade", 1, 0, 'C', fill=True)
    pdf.cell(25, 12, "Result", 1, 0, 'C', fill=True)
    pdf.cell(65, 12, "Suggestion", 1, 1, 'C', fill=True)

    # Table Rows
    fill = False
    for sub, mark in marks.items():
        pdf.set_fill_color(255, 255, 255) if not fill else pdf.set_fill_color(245, 245, 245)
        fill = not fill
        pdf.set_text_color(0,0,0)
        pdf.cell(50, 10, sub, 1, 0, 'C', fill=True)
        pdf.cell(25, 10, str(mark), 1, 0, 'C', fill=True)
        pdf.cell(25, 10, grade(mark), 1, 0, 'C', fill=True)
        pdf.cell(25, 10, pass_fail(mark), 1, 0, 'C', fill=True)
        pdf.cell(65, 10, suggestion(mark), 1, 1, 'C', fill=True)

    if student_type == "School Student":
        pdf.ln(3)
        pdf.cell(0,10,f"Engineering Cutoff: {engineering_cutoff}", ln=True)
        if medical_cutoff != "N/A":
            pdf.cell(0,10,f"Medical Cutoff: {medical_cutoff}", ln=True)

    pdf_output = f"{name}_marksheet.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        st.download_button("📥 Download Marksheet PDF", f, file_name=pdf_output, mime="application/pdf")
