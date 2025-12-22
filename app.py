import streamlit as st
import pandas as pd
import requests, base64, tempfile
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ---------------- EMAILJS CONFIG ----------------
EMAILJS_SERVICE_ID = "YOUR_SERVICE_ID"
EMAILJS_TEMPLATE_ID = "YOUR_TEMPLATE_ID"
EMAILJS_PUBLIC_KEY = "YOUR_PUBLIC_KEY"

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Student Marksheet Portal", layout="wide")

# ---------------- CUSTOM THEME ----------------
st.markdown("""
<style>
body {background-color: #f0f8ff;}
h1, h2, h3 {color: #1f4e79;}
.stButton>button {background-color:#1f4e79;color:white;border-radius:10px;}
.stTextInput input,.stNumberInput input,.stSelectbox div {background:white;color:black;}
table,th,td {color:black;}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1 style='text-align:center;'>📘 STUDENT MARKSHEET PORTAL</h1>", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def grade(m):
    if m >= 90: return "A+"
    elif m >= 80: return "A"
    elif m >= 70: return "B+"
    elif m >= 60: return "B"
    elif m >= 50: return "C"
    elif m >= 40: return "D"
    else: return "F"

# ---------------- STUDENT TYPE ----------------
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])

# ---------------- STUDENT DETAILS ----------------
st.subheader("👤 Student Details")
c1, c2 = st.columns([3,1])
with c1:
    name = st.text_input("Student Name")
    roll = st.text_input("Roll Number")
    attendance = st.number_input("Attendance Percentage", 0, 100)
    parent_mobile = st.text_input("Parent Mobile Number")
    parent_email = st.text_input("Parent Email")
with c2:
    photo = st.file_uploader("Upload Student Photo", ["jpg","png"])
    if photo:
        st.image(photo, width=120)

# ---------------- SUBJECT SELECTION ----------------
if student_type == "School Student":
    group = st.selectbox("Group", ["Biology","Computer Science","Commerce","History"])
    subject_map = {
        "Biology": ["Tamil","English","Maths","Physics","Chemistry","Biology"],
        "Computer Science": ["Tamil","English","Maths","Physics","Chemistry","Computer Science"],
        "Commerce": ["Tamil","English","Accountancy","Economics","Commerce","Maths"],
        "History": ["Tamil","English","History","Civics","Geography","Economics"]
    }
    subjects = subject_map[group]
else:
    dept = st.selectbox("Department", ["CSE","ECE","Biotechnology"])
    sem = st.selectbox("Semester", [f"Semester {i}" for i in range(1,9)])
    dept_map = {
        "CSE": ["Maths","Python","DSA","OS","DBMS","Networks"],
        "ECE": ["Maths","Circuits","Signals","VLSI","Embedded","Control"],
        "Biotechnology": ["Biochem","Genetics","Microbiology","Immunology","Bioinformatics","Bioprocess"]
    }
    subjects = dept_map[dept]

# ---------------- MARK ENTRY ----------------
st.subheader("✍️ Enter Marks")
marks = {}
for s in subjects:
    marks[s] = st.number_input(s, 0, 100, step=1, key=s)

# ---------------- MARKSHEET TABLE ----------------
df = pd.DataFrame({
    "Subject": subjects,
    "Marks": marks.values()
})
df["Grade"] = df["Marks"].apply(grade)
df["Result"] = df["Marks"].apply(lambda x: "PASS" if x >= 40 else "FAIL")

total = df["Marks"].sum()
average = df["Marks"].mean()

st.subheader("📊 Marksheet Preview")
st.dataframe(df)

remark = "Excellent" if average >= 75 else "Good" if average >= 50 else "Needs Improvement"
st.success(f"Total: {total}")
st.info(f"Average: {average:.2f}%")
st.warning(f"Teacher Remark: {remark}")

# ---------------- PDF GENERATION ----------------
def build_pdf():
    file = "marksheet.pdf"
    doc = SimpleDocTemplate(file)
    styles = getSampleStyleSheet()
    elems = []

    elems.append(Paragraph("<b>STUDENT MARKSHEET</b>", styles["Title"]))
    elems.append(Paragraph(f"Name: {name}", styles["Normal"]))
    elems.append(Paragraph(f"Roll No: {roll}", styles["Normal"]))
    elems.append(Paragraph(f"Attendance: {attendance}%", styles["Normal"]))
    elems.append(Paragraph(f"Parent Email: {parent_email}", styles["Normal"]))
    elems.append(Paragraph("<br/>", styles["Normal"]))

    if photo:
        with tempfile.NamedTemporaryFile(delete=False) as t:
            t.write(photo.read())
            elems.append(Image(t.name, width=90, height=110))

    table_data = [["Subject","Marks","Grade","Result"]] + df.values.tolist()
    table = Table(table_data)
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.lightblue),
        ("GRID",(0,0),(-1,-1),1,colors.grey)
    ]))
    elems.append(table)
    elems.append(Paragraph(f"Teacher Remark: {remark}", styles["Normal"]))

    doc.build(elems)
    return file

# ---------------- EMAIL SEND ----------------
def send_email(parent_email, pdf_path):
    with open(pdf_path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()

    payload = {
        "service_id": EMAILJS_SERVICE_ID,
        "template_id": EMAILJS_TEMPLATE_ID,
        "user_id": EMAILJS_PUBLIC_KEY,
        "template_params": {
            "to_email": parent_email,
            "student_name": name,
            "message": "Please find attached marksheet.",
            "attachment": encoded
        }
    }

    r = requests.post("FHpdQbl_lVBlz9m8e", json=payload)
    return r.status_code == 200

# ---------------- BUTTONS ----------------
if st.button("📄 Download Marksheet PDF"):
    pdf = build_pdf()
    with open(pdf,"rb") as f:
        st.download_button("⬇️ Download PDF", f, "marksheet.pdf")

if st.button("📧 Send Marksheet to Parent Email"):
    pdf = build_pdf()
    if send_email(parent_email, pdf):
        st.success("📨 Marksheet sent successfully to parent email")
    else:
        st.error("❌ Email sending failed")
