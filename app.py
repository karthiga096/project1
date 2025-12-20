import streamlit as st
from fpdf import FPDF
import tempfile
import os
import unicodedata

# -------------------------------------------------
# BULLETPROOF TEXT SANITIZER (DO NOT CHANGE)
# -------------------------------------------------
def safe(text):
    if text is None:
        return ""
    text = str(text)
    text = unicodedata.normalize("NFKD", text)
    return text.encode("latin-1", "ignore").decode("latin-1")

# -------------------------------------------------
# GRADE LOGIC
# -------------------------------------------------
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

# -------------------------------------------------
# REMARK LOGIC (ASCII ONLY)
# -------------------------------------------------
def remark(mark):
    if mark >= 90:
        return "Excellent"
    elif mark >= 75:
        return "Very Good"
    elif mark >= 60:
        return "Good"
    elif mark >= 50:
        return "Average"
    else:
        return "Needs Improvement"

# -------------------------------------------------
# STREAMLIT UI
# -------------------------------------------------
st.set_page_config(page_title="Student Marksheet", layout="centered")
st.title("Student Marksheet Generator")

school = st.text_input("School / College Name")
student = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.number_input("Attendance Percentage", 0, 100, 75)

st.subheader("Enter Marks")

marks = []
for i in range(1, 6):
    marks.append(st.number_input(f"Subject {i}", 0, 100, 0))

total = sum(marks)
average = total / len(marks)

# -------------------------------------------------
# PDF GENERATION
# -------------------------------------------------
if st.button("Generate Marksheet PDF"):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)

    # Header
    pdf.cell(0, 10, safe(school.upper()), ln=True, align="C")
    pdf.ln(4)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, safe("STUDENT MARKSHEET"), ln=True, align="C")
    pdf.ln(10)

    # Student Info
    pdf.set_font("Arial", "", 11)
    pdf.cell(50, 8, safe("Student Name"), 0)
    pdf.cell(0, 8, safe(student), ln=True)

    pdf.cell(50, 8, safe("Roll Number"), 0)
    pdf.cell(0, 8, safe(roll), ln=True)

    pdf.cell(50, 8, safe("Attendance"), 0)
    pdf.cell(0, 8, safe(f"{attendance} %"), ln=True)

    pdf.ln(6)

    # Table Header
    pdf.set_font("Arial", "B", 11)
    headers = ["Subject", "Marks", "Grade", "Result", "Remark"]
    widths = [40, 25, 25, 25, 55]

    for h, w in zip(headers, widths):
        pdf.cell(w, 8, safe(h), 1)
    pdf.ln()

    # Table Rows
    pdf.set_font("Arial", "", 11)
    for i, m in enumerate(marks, start=1):
        g, r = grade(m)
        row = [f"Subject {i}", m, g, r, remark(m)]

        for item, w in zip(row, widths):
            pdf.cell(w, 8, safe(item), 1)
        pdf.ln()

    pdf.ln(4)

    # Summary
    pdf.set_font("Arial", "B", 11)
    pdf.cell(60, 8, safe("Total Marks"), 1)
    pdf.cell(0, 8, safe(total), 1, ln=True)

    pdf.cell(60, 8, safe("Average"), 1)
    pdf.cell(0, 8, safe(f"{average:.2f}"), 1, ln=True)

    result = "PASS" if average >= 50 else "FAIL"
    pdf.cell(60, 8, safe("Final Result"), 1)
    pdf.cell(0, 8, safe(result), 1, ln=True)

    # Save PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        pdf.output(tmp.name)
        path = tmp.name

    st.success("Marksheet PDF Generated Successfully")

    with open(path, "rb") as f:
        st.download_button(
            "Download Marksheet PDF",
            f,
            file_name="marksheet.pdf",
            mime="application/pdf"
        )

    os.remove(path)
