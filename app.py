import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF

# ================= PAGE SETTINGS =================
st.set_page_config(
    page_title="Student Marksheet Portal",
    layout="wide"
)

st.markdown(
    "<h1 style='text-align:center;color:#1E88E5;'>🎓 Student Marksheet Portal</h1>",
    unsafe_allow_html=True
)
st.markdown("<hr>", unsafe_allow_html=True)

# ================= BASIC DETAILS =================
st.subheader("👤 Student Details")

student_type = st.selectbox(
    "Student Type",
    ["School Student", "College Student"]
)

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Student Name")
    roll = st.text_input("Roll / Register Number")
with col2:
    attendance = st.number_input("Attendance Percentage", 0, 100)
    parent_email = st.text_input("Parent Email ID")

# ================= FUNCTIONS =================
def pass_fail(mark):
    return "Pass" if mark >= 35 else "Fail"

def grade(mark):
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
    else:
        return "D"

def remark(mark):
    if mark >= 75:
        return "Excellent"
    elif mark >= 50:
        return "Good"
    else:
        return "Needs Improvement"

df = None
subjects = []
marks = []

# ================= SCHOOL MODULE =================
if student_type == "School Student":
    st.subheader("🏫 School Academic Details")

    group = st.selectbox(
        "Select Group",
        ["Biology", "Computer Science", "Commerce", "Arts"]
    )

    subjects_map = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }

    subjects = subjects_map[group]

    st.markdown("### ✏️ Enter Marks")
    for sub in subjects:
        marks.append(st.number_input(sub, 0, 100, key=sub))

    if st.button("📊 Generate School Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [pass_fail(m) for m in marks],
            "Remark": [remark(m) for m in marks]
        })

        st.success("Marksheet Generated Successfully")
        st.dataframe(df, use_container_width=True)

        st.info(f"Total Marks : {sum(marks)}")
        st.info(f"Average : {np.mean(marks):.2f}")

# ================= COLLEGE MODULE =================
if student_type == "College Student":
    st.subheader("🎓 College Academic Details")

    department = st.selectbox(
        "Department",
        ["CSE", "ECE", "Biotechnology"]
    )
    semester = st.selectbox(
        "Semester",
        [f"Semester {i}" for i in range(1, 9)]
    )

    dept_subjects = {
        "CSE": ["Maths", "DS", "OS", "DBMS", "CN", "AI"],
        "ECE": ["Maths", "Signals", "Networks", "VLSI", "Embedded", "Control"],
        "Biotechnology": ["Biochemistry", "Genetics", "Microbiology", "Cell Biology", "Biostatistics", "Bioinformatics"]
    }

    subjects = dept_subjects[department]

    st.markdown("### ✏️ Enter Marks")
    for sub in subjects:
        marks.append(st.number_input(sub, 0, 100, key=sub + semester))

    if st.button("📊 Generate College Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [pass_fail(m) for m in marks],
            "Remark": [remark(m) for m in marks]
        })

        st.success("Marksheet Generated Successfully")
        st.dataframe(df, use_container_width=True)

# ================= PDF DOWNLOAD =================
if df is not None and st.button("📥 Download Marksheet PDF"):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "STUDENT MARKSHEET", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name : {name}", ln=True)
    pdf.cell(0, 8, f"Roll No : {roll}", ln=True)
    pdf.cell(0, 8, f"Attendance : {attendance}%", ln=True)
    pdf.cell(0, 8, f"Parent Email : {parent_email}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 11)
    pdf.cell(50, 8, "Subject", 1)
    pdf.cell(25, 8, "Marks", 1)
    pdf.cell(25, 8, "Grade", 1)
    pdf.cell(30, 8, "Result", 1)
    pdf.cell(60, 8, "Remark", 1)
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", "", 11)
    for i in range(len(df)):
        pdf.cell(50, 8, df.iloc[i]["Subject"], 1)
        pdf.cell(25, 8, str(df.iloc[i]["Marks"]), 1)
        pdf.cell(25, 8, df.iloc[i]["Grade"], 1)
        pdf.cell(30, 8, df.iloc[i]["Result"], 1)
        pdf.cell(60, 8, df.iloc[i]["Remark"], 1)
        pdf.ln()

    file_name = "Marksheet.pdf"
    pdf.output(file_name)

    with open(file_name, "rb") as f:
        st.download_button(
            "⬇️ Click to Download PDF",
            f,
            file_name=file_name,
            mime="application/pdf"
        )

    st.success("PDF ready for download!")
