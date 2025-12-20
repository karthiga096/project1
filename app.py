import streamlit as st
from fpdf import FPDF
import pandas as pd
from PIL import Image

# ----------------- Page Config -----------------
st.set_page_config(page_title="Student Marksheet Portal", layout="wide")

# ----------------- Custom CSS -----------------
st.markdown(
    """
    <style>
    .stApp {background-color: #E6F2FF; color: black;}
    h1, h2, h3, h4, h5, h6 {color: black; font-weight: bold;}
    label, .stMarkdown p, .stTextInput label, .stNumberInput label {color: black !important; font-weight: bold;}
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input,
    .stSelectbox>div>div>select,
    .stFileUploader>div>div>input {color: black !important; background-color: white !important; border: 2px solid #000000 !important; font-weight: bold;}
    .stTable td, .stTable th {color: black !important; background-color: white !important;}
    .stButton>button {background-color: #4CAF50; color: white; font-weight: bold; border-radius: 10px; padding: 8px 16px;}
    </style>
    """, unsafe_allow_html=True
)

st.title("🎓 Student Mark Generation Portal")

# ----------------- Inputs -----------------
college_name = st.text_input("Enter College/School Name", "KAMARAJ COLLEGE OF ENGINEERING AND TECHNOLOGY")
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", 0, 100, 90)
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")
photo_file = st.file_uploader("Upload Student Photo", type=["png", "jpg", "jpeg"])

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
    if mark >= 75: return "Excellent performance"
    elif mark >= 50: return "Average, work harder"
    else: return "Failed, must retake"

def emoji_feedback(mark):
    if mark >= 75: return "😄"
    elif mark >= 50: return "😐"
    else: return "😢"

# ----------------- Subjects -----------------
school_groups = {
    "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
    "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
    "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
    "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
}

college_departments = {
    "CSE": {"Semester 1": ["Maths", "Physics", "Programming", "Electronics", "English", "Lab"],
            "Semester 2": ["Maths 2", "Data Structures", "Physics 2", "DBMS", "English", "Lab"]},
    "ECE": {"Semester 1": ["Maths", "Physics", "Circuits", "Electronics", "English", "Lab"],
            "Semester 2": ["Maths 2", "Signals", "Electronics 2", "Communication", "English", "Lab"]},
    "Biotechnology": {"Semester 1": ["Biology", "Chemistry", "Maths", "Physics", "English", "Lab"],
                      "Semester 2": ["Genetics", "Microbiology", "Chemistry 2", "Maths 2", "English", "Lab"]}
}

marks = {}

# ----------------- Inputs for Subjects -----------------
if student_type == "School Student":
    group = st.selectbox("Select Group", list(school_groups.keys()))
    subjects = school_groups[group]
    st.subheader("Enter Subject Marks")
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
    dept = st.selectbox("Select Department", list(college_departments.keys()))
    sem = st.selectbox("Select Semester", list(college_departments[dept].keys()))
    subjects = college_departments[dept][sem]
    st.subheader("Enter Subject Marks")
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100, 0)

# ----------------- Generate Marksheet -----------------
if st.button("Generate Marksheet"):
    st.subheader("📝 Marksheet")
    data = []
    for sub, mark in marks.items():
        data.append({"Subject": sub, "Marks": mark, "Grade": grade(mark),
                     "Result": pass_fail(mark), "Suggestion": suggestion(mark),
                     "Emoji": emoji_feedback(mark)})
    df = pd.DataFrame(data)
    st.table(df)

    if student_type == "School Student":
        st.markdown(f"**Total Marks:** {total}")
        st.markdown(f"**Average Marks:** {average:.2f}")
        st.markdown(f"**Engineering Cutoff:** {engineering_cutoff}")
        if medical_cutoff != "N/A":
            st.markdown(f"**Medical Cutoff:** {medical_cutoff}")

    # ----------------- PDF Generation -----------------
    pdf = FPDF()
    pdf.add_page()

    # Unicode font for emojis
    pdf.add_font("DejaVu", "", "DejaVuSans.ttf", uni=True)
    pdf.set_font("DejaVu", 'B', 16)

    pdf.cell(0, 10, college_name, ln=True, align="C")
    pdf.cell(0, 10, "Student Marksheet", ln=True, align="C")
    pdf.ln(5)

    # Student Photo
    if photo_file is not None:
        image = Image.open(photo_file)
        image_path = "temp_photo.png"
        image.save(image_path)
        pdf.image(image_path, x=160, y=10, w=30, h=30)

    pdf.set_font("DejaVu", '', 12)
    pdf.set_text_color(0,0,0)

    pdf.cell(0, 8, f"Name: {name}", ln=True, fill=True)
    pdf.cell(0, 8, f"Roll Number: {roll}", ln=True, fill=True)
    pdf.cell(0, 8, f"Attendance: {attendance}%", ln=True, fill=True)
    pdf.cell(0, 8, f"Parent Email: {parent_email}", ln=True, fill=True)
    pdf.cell(0, 8, f"Parent Mobile: {parent_mobile}", ln=True, fill=True)
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(200,200,200)
    pdf.cell(50, 8, "Subject", 1, 0, 'C', fill=True)
    pdf.cell(25, 8, "Marks", 1, 0, 'C', fill=True)
    pdf.cell(25, 8, "Grade", 1, 0, 'C', fill=True)
    pdf.cell(25, 8, "Result", 1, 0, 'C', fill=True)
    pdf.cell(45, 8, "Suggestion", 1, 0, 'C', fill=True)
    pdf.cell(15, 8, "Emoji", 1, 1, 'C', fill=True)

    # Table Rows with colored boxes
    for sub, mark in marks.items():
        # Set cell color based on marks
        if mark >= 75:
            pdf.set_fill_color(144, 238, 144)  # Light green
        elif mark >= 50:
            pdf.set_fill_color(255, 255, 153)  # Light yellow
        else:
            pdf.set_fill_color(255, 160, 122)  # Light red

        pdf.set_text_color(0,0,0)  # letters always black
        pdf.cell(50, 8, sub, 1, 0, 'C', fill=True)
        pdf.cell(25, 8, str(mark), 1, 0, 'C', fill=True)
        pdf.cell(25, 8, grade(mark), 1, 0, 'C', fill=True)
        pdf.cell(25, 8, pass_fail(mark), 1, 0, 'C', fill=True)
        pdf.cell(45, 8, suggestion(mark), 1, 0, 'C', fill=True)
        pdf.cell(15, 8, emoji_feedback(mark), 1, 1, 'C', fill=True)

    if student_type == "School Student":
        pdf.ln(3)
        pdf.cell(0,8,f"Engineering Cutoff: {engineering_cutoff}", ln=True)
        if medical_cutoff != "N/A":
            pdf.cell(0,8,f"Medical Cutoff: {medical_cutoff}", ln=True)

    pdf_output = f"{name}_marksheet.pdf"
    pdf.output(pdf_output)

    with open(pdf_output, "rb") as f:
        st.download_button("📥 Download Marksheet PDF", f, file_name=pdf_output, mime="application/pdf")
