import streamlit as st
import pandas as pd
import numpy as np
from fpdf import FPDF
from io import BytesIO

# ================= PAGE CONFIG =================
st.set_page_config(page_title="Student Marksheet Portal", layout="wide")

# ================= CUSTOM CSS =================
st.markdown("""
<style>
body {
    background: linear-gradient(to right, #E3F2FD, #FFFFFF);
}
.card {
    background-color: #FFFFFF;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
h1, h2, h3 {
    color: #0D47A1;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>🎓 Student Marksheet Portal</h1>", unsafe_allow_html=True)

# ================= STUDENT DETAILS =================
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("👤 Student Details")

student_type = st.selectbox("Student Type", ["School Student", "College Student"])

col1, col2 = st.columns(2)
with col1:
    name = st.text_input("Student Name")
    roll = st.text_input("Roll / Register Number")
with col2:
    attendance = st.number_input("Attendance Percentage", 0, 100)
    parent_email = st.text_input("Parent Email")

st.markdown("</div>", unsafe_allow_html=True)

# ================= FUNCTIONS =================
def pass_fail(mark):
    return "Pass" if mark >= 35 else "Fail"

def grade(mark):
    if mark >= 90: return "A+"
    elif mark >= 80: return "A"
    elif mark >= 70: return "B+"
    elif mark >= 60: return "B"
    elif mark >= 50: return "C"
    else: return "D"

def remark(mark):
    if mark >= 75: return "Excellent"
    elif mark >= 50: return "Good"
    else: return "Needs Improvement"

df = None
subjects, marks = [], []

# ================= SCHOOL MODULE =================
if student_type == "School Student":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("🏫 School Academic Details")

    group = st.selectbox("Group", ["Biology", "Computer Science", "Commerce", "Arts"])

    subjects_map = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "Arts": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }

    subjects = subjects_map[group]

    for sub in subjects:
        marks.append(st.number_input(sub, 0, 100, key=sub))

    if st.button("📊 Generate Marksheet"):
        df = pd.DataFrame({
            "Subject": subjects,
            "Marks": marks,
            "Grade": [grade(m) for m in marks],
            "Result": [pass_fail(m) for m in marks],
            "Remark": [remark(m) for m in marks]
        })

        st.success("Marksheet Generated")
        st.dataframe(df, use_container_width=True)

        st.info(f"Total Marks: {sum(marks)}")
        st.info(f"Average: {np.mean(marks):.2f}")

    st.markdown("</div>", unsafe_allow_html=True)

# ================= REAL-TIME PDF DOWNLOAD =================
if df is not None:
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.subheader("📄 Download Marksheet")

    if st.button("📥 Generate & Download PDF"):
        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial", "B", 16)
        pdf.cell(0, 10, "STUDENT MARKSHEET", ln=True, align="C")
        pdf.ln(5)

        pdf.set_font("Arial", "", 12)
        pdf.cell(0, 8, f"Name: {name}", ln=True)
        pdf.cell(0, 8, f"Roll No: {roll}", ln=True)
        pdf.cell(0, 8, f"Attendance: {attendance}%", ln=True)
        pdf.cell(0, 8, f"Parent Email: {parent_email}", ln=True)
        pdf.ln(5)

        pdf.set_font("Arial", "B", 11)
        pdf.cell(50, 8, "Subject", 1)
        pdf.cell(25, 8, "Marks", 1)
        pdf.cell(25, 8, "Grade", 1)
        pdf.cell(30, 8, "Result", 1)
        pdf.cell(60, 8, "Remark", 1)
        pdf.ln()

        pdf.set_font("Arial", "", 11)
        for _, row in df.iterrows():
            pdf.cell(50, 8, row["Subject"], 1)
            pdf.cell(25, 8, str(row["Marks"]), 1)
            pdf.cell(25, 8, row["Grade"], 1)
            pdf.cell(30, 8, row["Result"], 1)
            pdf.cell(60, 8, row["Remark"], 1)
            pdf.ln()

        # REAL-TIME PDF (memory)
        pdf_bytes = pdf.output(dest="S").encode("latin-1")

        st.download_button(
            label="⬇️ Download Marksheet PDF",
            data=pdf_bytes,
            file_name="Marksheet.pdf",
            mime="application/pdf"
        )

        st.success("PDF generated in real time!")

    st.markdown("</div>", unsafe_allow_html=True)
