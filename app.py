import streamlit as st
import pandas as pd
from fpdf import FPDF

# ---------------- PAGE THEME ----------------
st.set_page_config(
    page_title="Marksheet Portal",
    layout="wide"
)

st.markdown("""
<style>
body {background-color: #f4f6f9;}
.big-title {font-size:40px; font-weight:bold; color:#2E86C1;}
.section {background-color:white; padding:20px; border-radius:12px; margin-bottom:20px;}
.sub-title {color:#117864; font-size:22px; font-weight:bold;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='big-title'>🎓 School & College Marksheet Generation Portal</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- BASIC DETAILS ----------------
st.markdown("<div class='section'>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>📌 Student Details</div>", unsafe_allow_html=True)

student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.slider("Attendance Percentage", 0, 100, 75)
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def grade(m):
    if m >= 90: return "A+"
    if m >= 80: return "A"
    if m >= 70: return "B+"
    if m >= 60: return "B"
    if m >= 50: return "C"
    return "D"

def result(m):
    return "Pass" if m >= 50 else "Fail"

def suggestion(m):
    if m >= 75: return "Excellent"
    if m >= 50: return "Need Improvement"
    return "Work Hard"

# ================== SCHOOL ==================
if student_type == "School Student":

    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>🏫 School Student Details</div>", unsafe_allow_html=True)

    group = st.selectbox("Select Group", ["Biology", "Computer Science", "Commerce", "History / Arts"])

    subjects_map = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }

    subjects = subjects_map[group]
    marks = []

    st.markdown("### ✏️ Enter Marks")
    for s in subjects:
        marks.append(st.number_input(s, 0, 100, 50))

    if st.button("📊 Generate School Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [result(m) for m in marks],
            "Suggestion": [suggestion(m) for m in marks]
        })

        st.success("Marksheet Generated")
        st.dataframe(df)

        total = sum(marks)
        avg = round(total / 6, 2)

        st.info(f"Total Marks: {total}")
        st.info(f"Average Marks: {avg}")

        if group in ["Biology", "Computer Science"]:
            eng_cutoff = marks[2] + (marks[3] + marks[4]) / 2
            st.warning(f"Engineering Cutoff: {round(eng_cutoff,2)}")

        if group == "Biology":
            med_cutoff = marks[5] + (marks[3] + marks[4]) / 2
            st.warning(f"Medical Cutoff: {round(med_cutoff,2)}")

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "School Marksheet", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Group: {group}", ln=True)
        pdf.cell(0, 8, f"Attendance: {attendance}%", ln=True)
        pdf.ln(5)

        for i in df.itertuples():
            pdf.cell(0, 8, f"{i.Subject} - {i.Marks} - {i.Grade} - {i.Result}", ln=True)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button("📥 Download PDF", pdf_bytes, "School_Marksheet.pdf")

    st.markdown("</div>", unsafe_allow_html=True)

# ================== COLLEGE ==================
if student_type == "College Student":

    st.markdown("<div class='section'>", unsafe_allow_html=True)
    st.markdown("<div class='sub-title'>🏛 College Student Details</div>", unsafe_allow_html=True)

    dept = st.selectbox("Select Department", ["CSE", "ECE", "Biotechnology"])
    sem = st.selectbox("Select Semester", [f"Semester {i}" for i in range(1,9)])

    marks = []
    st.markdown("### ✏️ Enter Marks")
    for i in range(1,7):
        marks.append(st.number_input(f"Subject {i}", 0, 100, 50))

    if st.button("📊 Generate College Marksheet"):
        df = pd.DataFrame({
            "Subject": [f"Subject {i}" for i in range(1,7)],
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [result(m) for m in marks],
            "Suggestion": [suggestion(m) for m in marks]
        })

        st.success("Marksheet Generated")
        st.dataframe(df)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "College Marksheet", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Department: {dept}", ln=True)
        pdf.cell(0, 8, f"{sem}", ln=True)

        for i in df.itertuples():
            pdf.cell(0, 8, f"{i.Subject} - {i.Marks} - {i.Grade} - {i.Result}", ln=True)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button("📥 Download PDF", pdf_bytes, "College_Marksheet.pdf")

    st.markdown("</div>", unsafe_allow_html=True)
