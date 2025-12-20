import streamlit as st
import pandas as pd
from fpdf import FPDF

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Marksheet Portal", layout="wide")

# ---------------- CUSTOM THEME ----------------
st.markdown("""
<style>
body {background-color: #F2F6FF;}
.title {font-size:42px; font-weight:bold; color:#1F4E79; text-align:center;}
.card {background-color:white; padding:25px; border-radius:15px;
       box-shadow: 0px 4px 10px rgba(0,0,0,0.1); margin-bottom:25px;}
.sub {font-size:24px; color:#117864; font-weight:bold;}
.good {color:green;}
.avg {color:orange;}
.fail {color:red;}
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='title'>🎓 School & College Marksheet Generation Portal</div>", unsafe_allow_html=True)
st.markdown("---")

# ---------------- STUDENT DETAILS ----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown("<div class='sub'>📌 Student Details</div>", unsafe_allow_html=True)

student_type = st.selectbox("Student Type", ["School Student", "College Student"])
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", min_value=0.0, max_value=100.0, step=0.1)
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

st.markdown("</div>", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def grade(m):
    if m >= 90: return "A+"
    elif m >= 80: return "A"
    elif m >= 70: return "B+"
    elif m >= 60: return "B"
    elif m >= 50: return "C"
    else: return "D"

def result(m):
    return "Pass" if m >= 50 else "Fail"

def suggestion(m):
    if m >= 75: return "Excellent performance"
    elif m >= 50: return "Can improve"
    else: return "Needs attention"

# ================= SCHOOL MODULE =================
if student_type == "School Student":

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>🏫 School Student Module</div>", unsafe_allow_html=True)

    group = st.selectbox("Select Group", ["Biology", "Computer Science", "Commerce", "History / Arts"])

    subject_map = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History / Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }

    subjects = subject_map[group]
    marks = []

    st.markdown("### ✏️ Enter Subject Marks")
    for sub in subjects:
        marks.append(st.number_input(sub, 0, 100, 50))

    if st.button("📊 Generate School Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [result(m) for m in marks],
            "Suggestion": [suggestion(m) for m in marks]
        })

        st.success("✅ Marksheet Generated Successfully")
        st.dataframe(df)

        total = sum(marks)
        avg = round(total / 6, 2)

        st.markdown(f"<h4 class='good'>Total Marks: {total}</h4>", unsafe_allow_html=True)
        st.markdown(f"<h4 class='avg'>Average Marks: {avg}</h4>", unsafe_allow_html=True)

        if group in ["Biology", "Computer Science"]:
            eng = marks[2] + (marks[3] + marks[4]) / 2
            st.markdown(f"<h4 class='good'>Engineering Cutoff: {round(eng,2)}</h4>", unsafe_allow_html=True)

        if group == "Biology":
            med = marks[5] + (marks[3] + marks[4]) / 2
            st.markdown(f"<h4 class='good'>Medical Cutoff: {round(med,2)}</h4>", unsafe_allow_html=True)

        # PDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "School Student Marksheet", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Attendance: {attendance}%", ln=True)
        pdf.ln(5)

        for i in df.itertuples():
            pdf.cell(0, 8, f"{i.Subject} - {i.Marks} - {i.Grade} - {i.Result}", ln=True)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button("📥 Download Marksheet PDF", pdf_bytes, "School_Marksheet.pdf")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= COLLEGE MODULE =================
if student_type == "College Student":

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>🏛 College Student Module</div>", unsafe_allow_html=True)

    dept = st.selectbox("Select Department", ["CSE", "ECE", "Biotechnology"])
    sem = st.selectbox("Select Semester", [f"Semester {i}" for i in range(1, 9)])

    marks = []
    st.markdown("### ✏️ Enter Subject Marks")
    for i in range(1, 7):
        marks.append(st.number_input(f"Subject {i}", 0, 100, 50))

    if st.button("📊 Generate College Marksheet"):
        df = pd.DataFrame({
            "Subject": [f"Subject {i}" for i in range(1, 7)],
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [result(m) for m in marks],
            "Suggestion": [suggestion(m) for m in marks]
        })

        st.success("✅ Marksheet Generated Successfully")
        st.dataframe(df)

        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "College Student Marksheet", ln=True, align="C")

        pdf.set_font("Arial", size=12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Department: {dept}", ln=True)
        pdf.cell(0, 8, f"{sem}", ln=True)

        for i in df.itertuples():
            pdf.cell(0, 8, f"{i.Subject} - {i.Marks} - {i.Grade} - {i.Result}", ln=True)

        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button("📥 Download Marksheet PDF", pdf_bytes, "College_Marksheet.pdf")

    st.markdown("</div>", unsafe_allow_html=True)
