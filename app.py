import streamlit as st
from fpdf import FPDF
from PIL import Image
import tempfile

# ----------------- PAGE CONFIG -----------------
st.set_page_config(
    page_title="Student Mark Portal",
    page_icon="🎓",
    layout="centered"
)

# ----------------- CUSTOM CSS -----------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(to right, #667eea, #764ba2);
    font-family: 'Segoe UI', sans-serif;
}
.main-title {
    text-align: center;
    color: white;
    font-size: 42px;
    font-weight: bold;
    margin-bottom: 10px;
}
.sub-title {
    text-align: center;
    color: #f1f1f1;
    font-size: 18px;
    margin-bottom: 30px;
}
.card {
    background-color: white;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0px 10px 30px rgba(0,0,0,0.25);
    margin-bottom: 25px;
}
.stButton>button {
    background: linear-gradient(to right, #ff512f, #dd2476);
    color: white;
    font-size: 18px;
    border-radius: 12px;
    height: 50px;
    width: 100%;
}
</style>
""", unsafe_allow_html=True)

# ----------------- PAGE HEADER -----------------
st.markdown("<div class='main-title'>🎓 Student Mark Generation Portal</div>", unsafe_allow_html=True)
st.markdown("<div class='sub-title'>Smart | Tabular | Professional Marksheet</div>", unsafe_allow_html=True)

# ----------------- STUDENT DETAILS -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
college = st.text_input("🏫 School / College Name")
student_type = st.selectbox("🎒 Student Type", ["School Student", "College Student"])
name = st.text_input("👨‍🎓 Student Name")
roll = st.text_input("🆔 Roll Number")
attendance = st.number_input("📊 Attendance Percentage", 0, 100)
photo = st.file_uploader("🖼 Upload Student Photo", type=["png", "jpg", "jpeg"])
st.markdown("</div>", unsafe_allow_html=True)

if photo:
    st.image(photo, width=180, caption="Student Photo")

# ----------------- SUBJECT MARKS INPUT -----------------
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.subheader("📚 Enter Subject Marks (0-100)")
subjects = ["Mathematics", "Science", "English", "Computer Science", "Social Science"]
marks = {}
for subj in subjects:
    marks[subj] = st.number_input(f"{subj}", 0, 100, step=1)
st.markdown("</div>", unsafe_allow_html=True)

# ----------------- RESULT & PDF -----------------
def grade_calc(mark):
    if mark >= 90:
        return "A+", (0, 128, 0)   # Green
    elif mark >= 75:
        return "A", (34, 139, 34)  # Dark Green
    elif mark >= 60:
        return "B", (255, 215, 0)  # Gold
    elif mark >= 50:
        return "C", (255, 165, 0)  # Orange
    else:
        return "Fail", (255, 0, 0) # Red

if st.button("✨ Generate Result & PDF"):

    total = sum(marks.values())
    avg = total / len(subjects)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # School name header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, college, ln=True, align="C")
    pdf.cell(0, 10, "Student Marksheet", ln=True, align="C")
    pdf.ln(10)

    # Student details
    pdf.set_font("Arial", "", 12)
    pdf.cell(50, 10, f"Name: {name}", border=1)
    pdf.cell(50, 10, f"Roll No: {roll}", border=1)
    pdf.cell(50, 10, f"Type: {student_type}", border=1)
    pdf.cell(0, 10, f"Attendance: {attendance}%", border=1, ln=True)

    # Add photo
    if photo:
        image = Image.open(photo)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image.save(tmp_file.name)
        pdf.image(tmp_file.name, x=150, y=30, w=40)  # Position top-right

    pdf.ln(15)

    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 10, "Subject", border=1, align="C")
    pdf.cell(30, 10, "Marks", border=1, align="C")
    pdf.cell(30, 10, "Grade", border=1, align="C")
    pdf.ln()

    # Table rows with colored grades
    pdf.set_font("Arial", "", 12)
    for subj, mark in marks.items():
        g, color = grade_calc(mark)
        pdf.set_fill_color(*color)
        pdf.cell(80, 10, subj, border=1)
        pdf.cell(30, 10, str(mark), border=1)
        pdf.cell(30, 10, g, border=1, ln=True, fill=True)

    # Total & Average
    total_grade, _ = grade_calc(avg)
    pdf.ln(5)
    pdf.cell(80, 10, "Total", border=1)
    pdf.cell(30, 10, str(total), border=1)
    pdf.cell(30, 10, "", border=1, ln=True)

    pdf.cell(80, 10, "Average", border=1)
    pdf.cell(30, 10, f"{avg:.2f}", border=1)
    pdf.cell(30, 10, total_grade, border=1, ln=True)

    # Save PDF temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf.output(tmp_pdf.name)
        st.success("✅ PDF Generated Successfully!")
        st.download_button(
            label="📥 Download Tabular Marksheet PDF",
            data=open(tmp_pdf.name, "rb").read(),
            file_name=f"{name}_marksheet.pdf",
            mime="application/pdf"
        )
