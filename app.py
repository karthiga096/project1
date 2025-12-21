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
.stButton>button {background-color:#8b004b; color:white; border-radius:10px; height:40px; width:200px;}
.stTextInput>div>div>input {border-radius:5px; border:1px solid #8b004b;}
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
inst_name = st.text_input("School / College Name")
inst_addr = st.text_input("Address")
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
    photo = st.file_uploader("Upload Student Photo", ["jpg","png"])
    if photo:
        st.image(photo, width=150, caption="Student Photo")

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
st.subheader("✍️ Enter Marks")
marks = {s: st.number_input(s, 0, 100, key=s) for s in subjects}

# ---------------- GENERATE MARKSHEET ----------------
if st.button("📄 Generate Marksheet"):

    df = pd.DataFrame({
        "Subject": subjects,
        "Marks": marks.values()
    })
    df["Grade"] = df["Marks"].apply(grade)
    df["Result"] = df["Marks"].apply(lambda x: "✅ PASS" if x >= 40 else "❌ FAIL")

    total = df["Marks"].sum()
    avg = df["Marks"].mean()

    st.subheader("📊 Marksheet Preview")
    # Colorful table
    def highlight(val):
        color = '#90ee90' if val >= 40 else '#ff7f7f'
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
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),1,colors.black)
        ]))
        elems.append(table)
        elems.append(Paragraph(f"<b>Teacher Remark:</b> {remark}", styles["Normal"]))
        doc.build(elems)
        return file

    pdf = build_pdf()
    with open(pdf,"rb") as f:
        st.download_button("⬇️ Download Marksheet PDF", f, "marksheet.pdf")

    # ---------------- EMAIL ----------------
    if st.checkbox("📧 Email PDF to Parent"):
        try:
            msg=EmailMessage()
            msg["Subject"]="Student Marksheet"
            msg["From"]="your_email@gmail.com"
            msg["To"]=parent_email
            msg.set_content("Attached marksheet")

            with open(pdf,"rb") as f:
                msg.add_attachment(f.read(), maintype="application", subtype="pdf", filename="marksheet.pdf")

            server=smtplib.SMTP_SSL("smtp.gmail.com",465)
            server.login("your_email@gmail.com","APP_PASSWORD")
            server.send_message(msg)
            server.quit()
            st.success("Email sent successfully")
        except:
            st.error("Email failed")
