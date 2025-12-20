import streamlit as st
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import tempfile

# ---------------- ATTRACTIVE THEME ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #667eea, #764ba2);
}
h1, h2, h3 {
    color: #ffffff;
    text-align: center;
}
label {
    color: #ffffff;
    font-weight: bold;
}
div[data-testid="stVerticalBlock"] {
    background-color: rgba(255,255,255,0.08);
    padding: 20px;
    border-radius: 15px;
}
.stButton > button {
    background: linear-gradient(to right, #ff512f, #f09819);
    color: white;
    font-size: 20px;
    border-radius: 12px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ---------------- GRADE FUNCTION ----------------
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

# ---------------- GPA FUNCTION ----------------
grade_points = {"A+":10, "A":9, "B+":8, "B":7, "C":6, "D":0}

def calculate_gpa(marks):
    return round(sum(grade_points[grade(m)[0]] for m in marks) / len(marks), 2)

# ---------------- ML SUGGESTION ----------------
def lr_suggestion(marks):
    X = np.array(range(1, 7)).reshape(-1, 1)
    y = np.array(marks)
    model = LinearRegression()
    model.fit(X, y)
    return "Performance Improving" if model.coef_[0] > 0 else "Needs More Practice"

# ---------------- SAVE TO EXCEL ----------------
def save_to_excel(data, filename="student_records.xlsx"):
    df = pd.DataFrame([data])
    if os.path.exists(filename):
        old = pd.read_excel(filename)
        df = pd.concat([old, df], ignore_index=True)
    df.to_excel(filename, index=False)

# ---------------- PDF GENERATION ----------------
def generate_pdf(name, roll, subjects, marks, student_type):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "STUDENT MARKSHEET", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name : {name}", ln=True)
    pdf.cell(0, 8, f"Roll No : {roll}", ln=True)
    pdf.ln(5)

    # Table Header
    pdf.set_font("Arial", "B", 11)
    pdf.cell(45, 10, "Subject", 1)
    pdf.cell(25, 10, "Marks", 1)
    pdf.cell(25, 10, "Grade", 1)
    pdf.cell(35, 10, "Result", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 11)

    overall_pass = True
    total = sum(marks)

    for sub, mark in zip(subjects, marks):
        g, r = grade(mark)
        if r == "Fail":
            overall_pass = False
        pdf.cell(45, 10, sub, 1)
        pdf.cell(25, 10, str(mark), 1)
        pdf.cell(25, 10, g, 1)
        pdf.cell(35, 10, r, 1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Total Marks : {total}", ln=True)
    pdf.cell(0, 8, f"Overall Result : {'PASS' if overall_pass else 'FAIL'}", ln=True)

    if student_type == "College Student":
        pdf.cell(0, 8, f"GPA : {calculate_gpa(marks)}", ln=True)

    pdf.cell(0, 8, f"ML Suggestion : {lr_suggestion(marks)}", ln=True)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    return temp.name

# ---------------- UI ----------------
st.title("🎓 Smart Marksheet Generation System")

student_type = st.selectbox("Select Student Type", ["College Student", "School Student"])

name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

st.subheader("📘 Enter Subject Marks")

subjects = ["Maths", "Science", "English", "History", "Computer", "Physics"]
marks = [st.number_input(sub, 0, 100) for sub in subjects]

# ---------------- BUTTON ----------------
if st.button("Generate Marksheet"):
    if not all([name, roll, parent_mobile, parent_email]):
        st.error("❌ Please fill all details")
    else:
        pdf_path = generate_pdf(name, roll, subjects, marks, student_type)

        if student_type == "College Student":
            save_to_excel({
                "Type": "College",
                "Name": name,
                "Roll": roll,
                "GPA": calculate_gpa(marks),
                "Parent Mobile": parent_mobile,
                "Parent Email": parent_email
            })
        else:
            save_to_excel({
                "Type": "School",
                "Name": name,
                "Roll": roll,
                "Total": sum(marks),
                "Parent Mobile": parent_mobile,
                "Parent Email": parent_email
            })

        st.success("✅ Marksheet Generated Successfully")

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download Marksheet PDF",
                f,
                file_name=f"{roll}_Marksheet.pdf",
                mime="application/pdf"
            )
