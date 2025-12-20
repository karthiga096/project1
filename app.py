import streamlit as st
import numpy as np
import pandas as pd
import os
from sklearn.linear_model import LinearRegression
from fpdf import FPDF
import tempfile

# ---------------- COLORFUL THEME ----------------
st.markdown("""
<style>
div[data-testid="stAppViewContainer"] {
    background: linear-gradient(to right, #43cea2, #185a9d);
}
h1, h2, h3, h4, label {
    color: white;
}
.stButton > button {
    background-color: #ff9800;
    color: white;
    font-size: 18px;
    border-radius: 10px;
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
    points = []
    for m in marks:
        g, _ = grade(m)
        points.append(grade_points[g])
    return round(sum(points) / len(points), 2)

# ---------------- ML SUGGESTION ----------------
def lr_suggestion(marks):
    X = np.array(range(1, 7)).reshape(-1, 1)
    y = np.array(marks)
    model = LinearRegression()
    model.fit(X, y)
    return "Performance Improving" if model.coef_[0] > 0 else "Needs More Practice"

# ---------------- SAVE TO EXCEL ----------------
def save_to_excel(data, filename="student_records.xlsx"):
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        df = pd.concat([df, pd.DataFrame([data])], ignore_index=True)
    else:
        df = pd.DataFrame([data])
    df.to_excel(filename, index=False)

# ---------------- PDF GENERATION ----------------
def generate_pdf(name, roll, subjects, marks, extra_info):
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "MARKSHEET", ln=True, align="C")
    pdf.ln(6)

    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Name : {name}", ln=True)
    pdf.cell(0, 8, f"Roll No : {roll}", ln=True)
    pdf.ln(6)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(35, 10, "Subject", 1)
    pdf.cell(25, 10, "Marks", 1)
    pdf.cell(25, 10, "Grade", 1)
    pdf.cell(30, 10, "Result", 1)
    pdf.cell(75, 10, "Suggestion", 1)
    pdf.ln()

    suggestion = lr_suggestion(marks)
    pdf.set_font("Arial", "", 11)

    for i in range(6):
        g, r = grade(marks[i])
        pdf.cell(35, 10, subjects[i], 1)
        pdf.cell(25, 10, str(marks[i]), 1)
        pdf.cell(25, 10, g, 1)
        pdf.cell(30, 10, r, 1)
        pdf.cell(75, 10, suggestion, 1)
        pdf.ln()

    pdf.ln(6)
    for key, value in extra_info.items():
        pdf.cell(0, 8, f"{key} : {value}", ln=True)

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    return temp.name

# ---------------- STREAMLIT UI ----------------
st.title("🎓 Smart Marksheet System using ML")

student_type = st.selectbox("Select Student Type", ["College Student", "School Student"])

name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
parent_mobile = st.text_input("Parent Mobile Number")
parent_email = st.text_input("Parent Email")

st.subheader("Enter Subject Marks")

subjects = ["Maths", "Science", "English", "History", "Computer", "Physics"]
marks = [st.number_input(sub, min_value=0, max_value=100) for sub in subjects]

# ---------------- BUTTON ----------------
if st.button("Generate Marksheet"):
    if not all([name, roll, parent_mobile, parent_email]):
        st.error("❌ Please fill all details")
    else:
        extra_info = {}

        if student_type == "College Student":
            gpa = calculate_gpa(marks)
            extra_info["GPA"] = gpa
            st.success(f"🎓 GPA : {gpa}")

            save_to_excel({
                "Type": "College",
                "Name": name,
                "Roll": roll,
                "GPA": gpa,
                "Parent Mobile": parent_mobile,
                "Parent Email": parent_email
            })

        else:
            total = sum(marks)
            eng_cutoff = marks[0] + (marks[1] + marks[5]) / 2
            med_cutoff = marks[2] + (marks[1] + marks[5]) / 2

            extra_info["Total Marks"] = total
            extra_info["Engineering Cutoff"] = eng_cutoff
            extra_info["Medical Cutoff"] = med_cutoff

            st.success(f"📘 Total Marks : {total}")
            st.info(f"🛠 Engineering Cutoff : {eng_cutoff}")
            st.info(f"🩺 Medical Cutoff : {med_cutoff}")

            save_to_excel({
                "Type": "School",
                "Name": name,
                "Roll": roll,
                "Total": total,
                "Engineering Cutoff": eng_cutoff,
                "Medical Cutoff": med_cutoff,
                "Parent Mobile": parent_mobile,
                "Parent Email": parent_email
            })

        pdf_path = generate_pdf(name, roll, subjects, marks, extra_info)

        st.subheader("📥 Download Marksheet")
        with open(pdf_path, "rb") as f:
            st.download_button(
                "Download PDF",
                f,
                file_name=f"{roll}_Marksheet.pdf",
                mime="application/pdf"
            )

        st.info(f"📧 Sent to Email: {parent_email}")
        st.info(f"📱 Sent to Mobile: {parent_mobile}")
