import streamlit as st
import pandas as pd
from fpdf import FPDF

st.set_page_config(page_title="Student Mark Portal", layout="wide")

st.markdown(
    "<h1 style='text-align:center;color:#4CAF50;'>🎓 Student Marksheet Generation Portal</h1>",
    unsafe_allow_html=True
)

student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])

name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", 0, 100)
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

# ---------- FUNCTIONS ----------
def grade(mark):
    if mark >= 90:
        return "A+", "Pass"
    elif mark >= 80:
        return "A", "Pass"
    elif mark >= 70:
        return "B+", "Pass"
    elif mark >= 60:
        return "B", "Pass"
    elif mark >= 50:
        return "C", "Pass"
    else:
        return "D", "Fail"

def color_mark(mark):
    if mark >= 75:
        return "🟢"
    elif mark >= 50:
        return "🟡"
    else:
        return "🔴"

# ---------- SCHOOL ----------
if student_type == "School Student":
    group = st.selectbox("Select Group", ["Biology", "Computer Science", "Commerce", "History"])

    group_subjects = {
        "Biology": ["Tamil","English","Maths","Physics","Chemistry","Biology"],
        "Computer Science": ["Tamil","English","Maths","Physics","Chemistry","Computer Science"],
        "Commerce": ["Tamil","English","Accountancy","Economics","Commerce","Maths"],
        "History": ["Tamil","English","History","Civics","Geography","Economics"]
    }

    subjects = group_subjects[group]
    marks = []

    st.subheader("Enter Subject Marks")
    for sub in subjects:
        marks.append(st.number_input(sub, 0, 100, key=sub))

    if st.button("Generate School Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Status": ["Pass" if m >= 35 else "Fail" for m in marks],
            "Indicator": [color_mark(m) for m in marks]
        })

        total = sum(marks)
        avg = total / len(marks)

        st.success("Marksheet Generated")
        st.dataframe(df)

        st.info(f"Total: {total} | Average: {avg:.2f}")

        if group == "Biology":
            eng_cutoff = marks[2] + (marks[3] + marks[4]) / 2
            med_cutoff = marks[5] + (marks[3] + marks[4]) / 2
            st.warning(f"Engineering Cutoff: {eng_cutoff}")
            st.warning(f"Medical Cutoff: {med_cutoff}")

# ---------- COLLEGE ----------
if student_type == "College Student":
    dept = st.selectbox("Department", ["CSE", "ECE", "Biotechnology"])
    sem = st.selectbox("Semester", [f"Sem {i}" for i in range(1, 9)])

    dept_subjects = {
        "CSE": ["Maths","DS","OS","DBMS","CN","AI"],
        "ECE": ["Maths","Signals","Networks","VLSI","Embedded","Control"],
        "Biotechnology": ["Biochem","Genetics","Microbiology","Cell Biology","Biostat","Bioinformatics"]
    }

    subjects = dept_subjects[dept]
    marks = []

    st.subheader("Enter Subject Marks")
    for sub in subjects:
        marks.append(st.number_input(sub, 0, 100, key=sub+sem))

    if st.button("Generate College Marksheet"):
        rows = []
        for s, m in zip(subjects, marks):
            g, r = grade(m)
            rows.append([s, m, g, r, color_mark(m)])

        df = pd.DataFrame(rows, columns=["Subject","Marks","Grade","Result","Indicator"])
        st.success("College Marksheet Generated")
        st.dataframe(df)

# ---------- PDF ----------
if st.button("Download Marksheet as PDF"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial","B",16)
    pdf.cell(0,10,"STUDENT MARKSHEET",ln=True,align="C")
    pdf.ln(10)

    pdf.set_font("Arial","",12)
    pdf.cell(0,8,f"Name: {name}",ln=True)
    pdf.cell(0,8,f"Roll No: {roll}",ln=True)
    pdf.cell(0,8,f"Attendance: {attendance}%",ln=True)
    pdf.cell(0,8,f"Parent Email: {parent_email}",ln=True)

    pdf.output("Marksheet.pdf")
    st.success("PDF Downloaded Successfully")
