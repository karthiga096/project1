import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from PIL import Image
import io

# ------------------ PAGE CONFIG ------------------
st.set_page_config(page_title="Mark Generation Portal", layout="wide")

st.title("🎓 School & College Student Mark Generation Portal")
st.markdown("---")

# ------------------ UTILITY FUNCTIONS ------------------

def get_grade(mark):
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

def get_result(mark):
    return "Pass" if mark >= 50 else "Fail"

def get_color(mark):
    if mark >= 75:
        return "Good"
    elif mark >= 50:
        return "Average"
    else:
        return "Fail"

def get_suggestion(mark):
    if mark >= 75:
        return "Excellent performance"
    elif mark >= 50:
        return "Can improve"
    else:
        return "Needs special attention"

# ------------------ INPUT SECTION ------------------

st.sidebar.header("📌 Student Details")

student_type = st.sidebar.selectbox("Select Student Type", ["School Student", "College Student"])

name = st.sidebar.text_input("Student Name")
roll = st.sidebar.text_input("Roll Number")
attendance = st.sidebar.slider("Attendance Percentage", 0, 100, 75)
parent_mobile = st.sidebar.text_input("Parent Mobile Number")
parent_email = st.sidebar.text_input("Parent Email")

# ------------------ SCHOOL STUDENT ------------------

if student_type == "School Student":

    group = st.sidebar.selectbox(
        "Select Group",
        ["Biology", "Computer Science", "Commerce", "History / Arts"]
    )

    subjects_map = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }

    subjects = subjects_map[group]
    marks = []

    st.subheader("✏️ Enter Subject Marks")

    for sub in subjects:
        marks.append(st.number_input(f"{sub} Marks", 0, 100, 50))

    if st.button("📊 Generate Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Result": [get_result(m) for m in marks],
            "Performance": [get_color(m) for m in marks],
            "Suggestion": [get_suggestion(m) for m in marks]
        })

        total = sum(marks)
        average = round(total / 6, 2)

        st.success("Marksheet Generated Successfully")
        st.dataframe(df)

        st.info(f"Total Marks: {total}")
        st.info(f"Average Marks: {average}")

        if group in ["Biology", "Computer Science"]:
            eng_cutoff = marks[2] + (marks[3] + marks[4]) / 2
            st.warning(f"Engineering Cutoff: {round(eng_cutoff,2)}")

        if group == "Biology":
            med_cutoff = marks[5] + (marks[3] + marks[4]) / 2
            st.warning(f"Medical Cutoff: {round(med_cutoff,2)}")

        # ------------------ PDF GENERATION ------------------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "School Student Marksheet", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Group: {group}", ln=True)
        pdf.cell(0, 8, f"Attendance: {attendance}%", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 11)
        for col in df.columns:
            pdf.cell(38, 8, col, border=1)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(38, 8, str(item), border=1)
            pdf.ln()

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            label="📥 Download Marksheet PDF",
            data=pdf_bytes,
            file_name="School_Marksheet.pdf",
            mime="application/pdf"
        )

# ------------------ COLLEGE STUDENT ------------------

if student_type == "College Student":

    dept = st.sidebar.selectbox("Select Department", ["CSE", "ECE", "Biotechnology"])
    semester = st.sidebar.selectbox("Select Semester", [f"Semester {i}" for i in range(1, 9)])

    subjects = [f"Subject {i}" for i in range(1, 7)]
    marks = []

    st.subheader("✏️ Enter Subject Marks")

    for sub in subjects:
        marks.append(st.number_input(f"{sub} Marks", 0, 100, 50))

    if st.button("📊 Generate Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Grade": [get_grade(m) for m in marks],
            "Result": [get_result(m) for m in marks],
            "Suggestion": [get_suggestion(m) for m in marks]
        })

        st.success("Marksheet Generated Successfully")
        st.dataframe(df)

        # ------------------ PDF ------------------
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "College Student Marksheet", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Department: {dept}", ln=True)
        pdf.cell(0, 8, f"{semester}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 11)
        for col in df.columns:
            pdf.cell(38, 8, col, border=1)
        pdf.ln()

        pdf.set_font("Arial", size=10)
        for _, row in df.iterrows():
            for item in row:
                pdf.cell(38, 8, str(item), border=1)
            pdf.ln()

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            label="📥 Download Marksheet PDF",
            data=pdf_bytes,
            file_name="College_Marksheet.pdf",
            mime="application/pdf"
        )
