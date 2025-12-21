import streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile
import smtplib
from email.message import EmailMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Marksheet Portal", layout="wide")

# ---------------- CUSTOM THEME ----------------
st.markdown("""
<style>
body {background-color: #fff0f5; font-family: 'Arial';}
h1, h2, h3 {color: #8b004b;}
.stButton>button {background-color:#8b004b; color:white; border-radius:8px; height:35px; width:180px;}
.stTextInput>div>div>input {border-radius:5px; border:1px solid #8b004b; height:30px;}
.stSlider>div>div>div>div {background-color:#fde6ef;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>📘 STUDENT MARKSHEET PORTAL</h1>", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def grade(m):
    if m >= 90: return "O"
    elif m >= 80: return "A+"
    elif m >= 70: return "A"
    elif m >= 60: return "B"
    elif m >= 50: return "C"
    elif m >= 40: return "D"
    else: return "F"

# ---------------- STUDENT TYPE ----------------
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])

# ---------------- INSTITUTE DETAILS ----------------
st.subheader("🏫 Institute Details")
col1, col2, col3 = st.columns([3,3,2])
with col1:
    inst_name = st.text_input("School / College Name")
with col2:
    inst_addr = st.text_input("Address")
with col3:
    year = st.text_input("Academic Year", "2024–2025")

# ---------------- STUDENT DETAILS ----------------
st.subheader("👤 Student Details")
col1, col2 = st.columns([3,1])
with col1:
    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    attendance = st.slider("Attendance %", 0, 100)
    parent_mobile = st.text_input("Parent Mobile")
    parent_email = st.text_input("Parent Email")
with col2:
    photo = st.file_uploader("Upload Photo", ["jpg","png"])
    if photo:
        st.image(photo, width=130, caption="Student Photo")

# ---------------- SUBJECT LOGIC ----------------
if student_type == "School Student":
    group = st.selectbox("Group", ["Biology", "Computer Science", "Commerce", "History"])
    if group == "Biology":
        subjects = ["English","Tamil","Maths","Physics","Chemistry","Biology"]
    elif group == "Computer Science":
        subjects = ["English","Tamil","Maths","Physics","Chemistry","Computer Science"]
    else:
        subjects = ["English","Tamil","Maths","Accountancy","Economics","Business Studies"]
else:
    dept = st.selectbox("Department", ["CSE","ECE","Biotechnology","AIML","Mechanical","Civil"])
    sem = st.selectbox("Semester", [f"Semester {i}" for i in range(1,9)])
    if dept == "CSE":
        subjects = ["Maths","Python","DSA","OS","DBMS","Networks"]
    elif dept == "ECE":
        subjects = ["Maths","Circuits","Signals","VLSI","Embedded","Control"]
    else:
        subjects = ["Biochem","Genetics","Microbio","Immunology","Bioinformatics","Bioprocess"]

# ---------------- MARK INPUT ----------------
st.subheader("✍️ Enter Marks (Real-time Preview)")
marks = {}
for s in subjects:
    marks[s] = st.number_input(s, 0, 100, key=s, step=1, format="%d")

# ---------------- REAL-TIME MARKSHEET ----------------
df = pd.DataFrame({
    "Subject": subjects,
    "Marks": marks.values()
})
df["Grade"] = df["Marks"].apply(grade)
df["Result"] = df["Marks"].apply(lambda x: "✅ PASS" if x >= 40 else "❌ FAIL")

total = df["Marks"].sum()
avg = df["Marks"].mean()

st.subheader("📊 Marksheet Preview")
# Color-coded table
def highlight(val):
    color = '#90ee90' if val >= 40 else '#ffb6c1'
    return f'background-color: {color}'
st.dataframe(df.style.applymap(highlight, subset=["Marks"]))

st.success(f"Total Marks: {total}")
st.info(f"Average: {avg:.2f}%")

# Remark
if avg>=75: remark="🌟 Excellent performance"
elif avg>=50: remark="👍 Good, can improve"
else: remark="⚠️ Needs improvement"
st.warning(f"Teacher Remark: {remark}")

# ---------------- PDF GENERATION ----------------
def build_pdf():
    file="marksheet.pdf"
    doc=SimpleDocTemplate(file)
    styles=getSampleStyleSheet()
    elems=[]

    elems.append(Paragraph(f"<b>{inst_name}</b>", styles["Title"]))
    elems.append(Paragraph(inst_addr, styles["Normal"]))
    elems.append(Paragraph(f"Academic Year: {year}", styles["Normal"]))
    elems.append(Paragraph("<br/>", styles["Normal"]))

    elems.append(Paragraph(f"Name: {name}", styles["Normal"]))
    elems.append(Paragraph(f"Roll No: {roll}", styles["Normal"]))
    elems.append(Paragraph(f"Attendance: {attendance}%", styles["Normal"]))
    elems.append(Paragraph(f"Parent Contact: {parent_mobile}", styles["Normal"]))
    elems.append(Paragraph(f"Email: {parent_email}", styles["Normal"]))

    if photo:
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(photo.read())
            elems.append(Image(t.name, width=90, height=110))

    table_data=[["Subject","Marks","Grade","Result"]]+df.values.tolist()
    table=Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightpink),
        ("TEXTCOLOR",(0,0),(-1,0),colors.black),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey)
    ]))
    elems.append(table)
    elems.append(Paragraph(f"<b>Teacher Remark:</b> {remark}", styles["Normal"]))
    doc.build(elems)
    return file

if st.button("📄 Download Marksheet PDF"):
    pdf = build_pdf()
    with open(pdf,"rb") as f:
        st.download_button("⬇️ Download PDF", f, "marksheet.pdf")
