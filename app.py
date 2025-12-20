import streamlit as st
from fpdf import FPDF
import pandas as pd

# ----------------- Helper Functions -----------------

def grade(mark):
    """Return grade based on marks"""
    if mark >= 90:
        return "A+"
    elif mark >= 80:
        return "A"
    elif mark >= 70:
        return "B+"
    elif mark >= 60:
        return "B"
    elif mark >= 50:
        return "C"
    elif mark >= 35:
        return "D"
    else:
        return "F"

def pass_fail(mark):
    """Return Pass/Fail based on marks"""
    return "Pass" if mark >= 35 else "Fail"

def suggestion(mark):
    """Return suggestion based on marks"""
    if mark >= 75:
        return "Excellent performance"
    elif mark >= 60:
        return "Good, keep improving"
    elif mark >= 50:
        return "Average, work harder"
    elif mark >= 35:
        return "Needs improvement"
    else:
        return "Failed, must retake"

def color_code(mark):
    """Return color for PDF table cell"""
    if mark >= 60:
        return (144, 238, 144)  # Green
    elif mark >= 35:
        return (255, 255, 102)  # Yellow
    else:
        return (255, 102, 102)  # Red

# ----------------- School Subjects -----------------
school_groups = {
    "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
    "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
    "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
    "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
}

# ----------------- College Subjects Example -----------------
college_departments = {
    "CSE": {
        "Semester 1": ["Maths", "Physics", "Programming", "Electronics", "English", "Lab"],
        "Semester 2": ["Maths 2", "Data Structures", "Physics 2", "DBMS", "English", "Lab"]
        # Add more semesters
    },
    "ECE": {
        "Semester 1": ["Maths", "Physics", "Circuits", "Electronics", "English", "Lab"],
        "Semester 2": ["Maths 2", "Signals", "Electronics 2", "Communication", "English", "Lab"]
    },
    "Biotechnology": {
        "Semester 1": ["Biology", "Chemistry", "Maths", "Physics", "English", "Lab"],
        "Semester 2": ["Genetics", "Microbiology", "Chemistry 2", "Maths 2", "English", "Lab"]
    }
}

# ----------------- Streamlit App -----------------
st.set_page_config(page_title="Student Marksheet Portal", layout="wide")
st.title("🎓 Student Mark Generation Portal")

# Common Inputs
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", 0, 100, 90)
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

marks = {}

if student_type == "School Student":
    group = st.selectbox("Select Group", list(school_groups.keys()))
    subjects = school_groups[group]

    st.subheader("Enter Subject Marks")
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100, 0)

    total = sum(marks.values())
    average = total / len(subjects)

    # School Cutoffs
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

# ----------------- Display Marksheet -----------------
if st.button("Generate Marksheet"):

    st.subheader("📝 Marksheet")
    data = []
    for sub, mark in marks.items():
        data.append({
            "Subject": sub,
            "Marks": mark,
            "Grade": grade(mark),
            "Result": pass_fail(mark),
            "Suggestion": suggestion(mark)
        })

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

    # Logo
    # pdf.image("school_logo.png", 10, 8, 33)  # Add logo if available

    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Student Marksheet", ln=True, align="C")
    pdf.ln(5)

    # Student Details
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 8, f"Name: {name}", ln=True)
    pdf.cell(0, 8, f"Roll Number: {roll}", ln=True)
    pdf.cell(0, 8, f"Attendance: {attendance}%", ln=True)
    pdf.cell(0, 8, f"Parent Email: {parent_email}", ln=True)
    pdf.cell(0, 8, f"Parent Mobile: {parent_mobile}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_fill_color(200,200,200)
    pdf.cell(60, 8, "Subject", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "Marks", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "Grade", 1, 0, 'C', fill=True)
    pdf.cell(30, 8, "Result", 1, 0, 'C', fill=True)
    pdf.cell(40, 8, "Suggestion", 1, 1, 'C', fill=True)

    # Table Rows
    for sub, mark in marks.items():
        r,g,b = color_code(mark)
        pdf.set_fill_color(r,g,b)
        pdf.cell(60, 8, sub, 1, 0, 'C')
        pdf.cell(30, 8, str(mark), 1, 0, 'C', fill=True)
        pdf.cell(30, 8, grade(mark), 1, 0, 'C', fill=True)
        pdf.cell(30, 8, pass_fail(mark), 1, 0, 'C', fill=True)
        pdf.cell(40, 8, suggestion(mark), 1, 1, 'C', fill=True)

    # School Cutoffs if applicable
    if student_type == "School Student":
        pdf.ln(3)
        pdf.cell(0,8,f"Engineering Cutoff: {engineering_cutoff}", ln=True)
        if medical_cutoff != "N/A":
            pdf.cell(0,8,f"Medical Cutoff: {medical_cutoff}", ln=True)

    # Save PDF
    pdf_output = f"{name}_marksheet.pdf"
    pdf.output(pdf_output)

    # Download Button
    with open(pdf_output, "rb") as f:
        st.download_button("📥 Download Marksheet PDF", f, file_name=pdf_output, mime="application/pdf")
