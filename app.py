import streamlit as st
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import tempfile

# ---------------- POSITIVE GREEN THEME ----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #d4fc79, #96e6a1);
}
h1, h2, h3 {
    color: #064420;
    text-align: center;
}
label {
    color: #064420;
    font-weight: bold;
}
div[data-testid="stVerticalBlock"] {
    background-color: rgba(255,255,255,0.85);
    padding: 20px;
    border-radius: 15px;
}
.stButton > button {
    background-color: #2ecc71;
    color: white;
    font-size: 18px;
    border-radius: 10px;
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

# ---------------- ML SUGGESTION ----------------
def lr_suggestion(marks):
    X = np.arange(1, len(marks)+1).reshape(-1, 1)
    model = LinearRegression()
    model.fit(X, marks)
    return "Overall Performance Improving 👍" if model.coef_[0] > 0 else "Needs Improvement 📘"

# ---------------- SAVE TO EXCEL ----------------
def save_to_excel(data, file="student_records.xlsx"):
    df = pd.DataFrame([data])
    if os.path.exists(file):
        old = pd.read_excel(file)
        df = pd.concat([old, df], ignore_index=True)
    df.to_excel(file, index=False)

# ---------------- PDF GENERATION ----------------
def generate_pdf(name, roll, subjects, marks, summary):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 12, "STUDENT MARKSHEET", ln=True, align="C")
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name : {name}", ln=True)
    pdf.cell(0, 8, f"Roll No : {roll}", ln=True)
    pdf.ln(4)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(50, 10, "Subject", 1)
    pdf.cell(30, 10, "Marks", 1)
    pdf.cell(30, 10, "Grade", 1)
    pdf.cell(40, 10, "Result", 1)
    pdf.ln()

    pdf.set_font("Arial", "", 11)
    overall_pass = True

    for s, m in zip(subjects, marks):
        g, r = grade(m)
        if r == "Fail":
            overall_pass = False
        pdf.cell(50, 10, s, 1)
        pdf.cell(30, 10, str(m), 1)
        pdf.cell(30, 10, g, 1)
        pdf.cell(40, 10, r, 1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 8, f"Overall Result : {'PASS' if overall_pass else 'FAIL'}", ln=True)

    for k, v in summary.items():
        pdf.cell(0, 8, f"{k} : {v}", ln=True)

    pdf.cell(0, 8, f"Suggestion : {lr_suggestion(marks)}", ln=True)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    return temp.name

# ---------------- UI ----------------
st.title("🎓 Smart School Marksheet System")

name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

group = st.selectbox("Select Group", ["Biology", "Computer Science", "History", "Commerce"])

# Subject Mapping
if group == "Biology":
    subjects = ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"]
elif group == "Computer Science":
    subjects = ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"]
elif group == "History":
    subjects = ["Tamil", "English", "History", "Civics", "Economics", "Geography"]
else:
    subjects = ["Tamil", "English", "Accountancy", "Business Maths", "Economics", "Commerce"]

marks = [st.number_input(sub, 0, 100) for sub in subjects]

# ---------------- BUTTON ----------------
if st.button("Generate Marksheet"):
    if not all([name, roll, parent_mobile, parent_email]):
        st.error("Please fill all details")
    else:
        total = sum(marks)
        average = round(total / len(marks), 2)

        summary = {
            "Total Marks": total,
            "Average": average
        }

        if group == "Biology":
            eng_cutoff = marks[2] + (marks[3] + marks[4]) / 2
            med_cutoff = marks[5] + (marks[3] + marks[4]) / 2
            summary["Engineering Cutoff"] = eng_cutoff
            summary["Medical Cutoff"] = med_cutoff

        elif group == "Computer Science":
            eng_cutoff = marks[2] + (marks[3] + marks[4]) / 2
            summary["Engineering Cutoff"] = eng_cutoff

        save_to_excel({
            "Name": name,
            "Roll": roll,
            "Group": group,
            "Total": total,
            "Average": average,
            "Parent Mobile": parent_mobile,
            "Parent Email": parent_email
        })

        pdf_path = generate_pdf(name, roll, subjects, marks, summary)

        st.success("✅ Marksheet Generated Successfully")

        with open(pdf_path, "rb") as f:
            st.download_button(
                "📥 Download Marksheet PDF",
                f,
                file_name=f"{roll}_Marksheet.pdf",
                mime="application/pdf"
            )
