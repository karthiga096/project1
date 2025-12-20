import streamlit as st
from fpdf import FPDF
import tempfile
import os

# ---------------- SAFE TEXT CLEANER ----------------
def clean_text(text):
    if text is None:
        return ""
    return str(text).encode("latin-1", "ignore").decode("latin-1")

# ---------------- GRADE FUNCTION ----------------
def grade(mark):
    if mark >= 90:
        return "A+", "PASS"
    elif mark >= 80:
        return "A", "PASS"
    elif mark >= 70:
        return "B+", "PASS"
    elif mark >= 60:
        return "B", "PASS"
    elif mark >= 50:
        return "C", "PASS"
    else:
        return "F", "FAIL"

# ---------------- SUGGESTION FUNCTION ----------------
def suggestion(mark):
    if mark >= 90:
        return "Excellent performance"
    elif mark >= 75:
        return "Very good. Practice more"
    elif mark >= 60:
        return "Good. Improve basics"
    elif mark >= 50:
        return "Average. Needs effort"
    else:
        return "Poor. Extra coaching required"

# ---------------- STREAMLIT UI ----------------
st.set_page_config(page_title="Student Marksheet Portal", layout="centered")

st.title("🎓 Student Marksheet Generation Portal")

college = st.text_input("College / School Name")
student_name = st.text_input("Student Name")
roll_no = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", 0, 100, 75)

st.subheader("Enter Subject Marks")

sub1 = st.number_input("Subject 1", 0, 100, 0)
sub2 = st.number_input("Subject 2", 0, 100, 0)
sub3 = st.number_input("Subject 3", 0, 100, 0)
sub4 = st.number_input("Subject 4", 0, 100, 0)
sub5 = st.number_input("Subject 5", 0, 100, 0)

marks = [sub1, sub2, sub3, sub4, sub5]
total = sum(marks)
average = total / 5

# ---------------- GENERATE PDF ----------------
if st.button("Generate Marksheet PDF"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)

    # Title
    pdf.cell(0, 10, clean_text(college.upper()), ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, clean_text("STUDENT MARKSHEET"), ln=True, align="C")
    pdf.ln(10)

    # Student Info
    pdf.set_font("Arial", "", 11)
    pdf.cell(50, 8, "Student Name:", 0)
    pdf.cell(0, 8, clean_text(student_name), ln=True)

    pdf.cell(50, 8, "Roll Number:", 0)
    pdf.cell(0, 8, clean_text(roll_no), ln=True)

    pdf.cell(50, 8, "Attendance:", 0)
    pdf.cell(0, 8, f"{attendance} %", ln=True)

    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 11)
    pdf.cell(40, 8, "Subject", 1)
    pdf.cell(30, 8, "Marks", 1)
    pdf.cell(30, 8, "Grade", 1)
    pdf.cell(30, 8, "Result", 1)
    pdf.cell(0, 8, "Remark", 1, ln=True)

    pdf.set_font("Arial", "", 11)

    for i, m in enumerate(marks, start=1):
        g, r = grade(m)
        pdf.cell(40, 8, f"Subject {i}", 1)
        pdf.cell(30, 8, str(m), 1)
        pdf.cell(30, 8, g, 1)
        pdf.cell(30, 8, r, 1)
        pdf.cell(0, 8, clean_text(suggestion(m)), 1, ln=True)

    pdf.ln(5)

    # Total & Average
    pdf.set_font("Arial", "B", 11)
    pdf.cell(60, 8, "Total Marks", 1)
    pdf.cell(0, 8, str(total), 1, ln=True)

    pdf.cell(60, 8, "Average Marks", 1)
    pdf.cell(0, 8, f"{average:.2f}", 1, ln=True)

    final_result = "PASS" if average >= 50 else "FAIL"
    pdf.cell(60, 8, "Final Result", 1)
    pdf.cell(0, 8, final_result, 1, ln=True)

    # Save PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        pdf_path = tmp.name

    st.success("✅ Marksheet PDF Generated Successfully")

    with open(pdf_path, "rb") as f:
        st.download_button(
            label="📄 Download Marksheet PDF",
            data=f,
            file_name="marksheet.pdf",
            mime="application/pdf"
        )

    os.remove(pdf_path)
