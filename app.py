import streamlit as st

# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="Student Mark Portal",
    page_icon="🎓",
    layout="centered"
)

# ---------- CUSTOM CSS ----------
st.markdown("""
<style>
/* Background */
.stApp {
    background: linear
Aimport streamlit as st
import pandas as pd
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import tempfile
import smtplib
from email.message import EmailMessage

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Marksheet Portal", layout="wide")

# ---------------- THEME ----------------
st.markdown("""
<style>
.main {background-color:#fde6ef;}
h1,h2,h3 {color:#8b004b;}
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
student_type = st.selectbox("Student Type", ["School Student", "College Student"])

# ---------------- INSTITUTE DETAILS ----------------
st.subheader("🏫 Institute Details")
inst_name = st.text_input("School / College Name")
inst_addr = st.text_input("Address")
year = st.text_input("Academic Year", "2024–2025")

# ---------------- STUDENT DETAILS ----------------
st.subheader("👤 Student Details")
name = st.text_input("Student Name")
roll = st.text_input("Roll Number")
attendance = st.slider("Attendance %", 0, 100)
parent_mobile = st.text_input("Parent Mobile")
parent_email = st.text_input("Parent Email")

photo = st.file_uploader("Upload Student Photo", ["jpg","png"])

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
    dept = st.selectbox("Department", ["CSE","ECE","Biotechnology"])
    sem = st.selectbox("Semester", [f"Semester {i}" for i in range(1,9)])

    if dept == "CSE":
        subjects = ["Maths","Python","DSA","OS","DBMS","Networks"]
    elif dept == "ECE":
        subjects = ["Maths","Circuits","Signals","VLSI","Embedded","Control"]
    else:
        subjects = ["Biochem","Genetics","Microbio","Immunology","Bioinformatics","Bioprocess"]

# ---------------- MARK INPUT ----------------
st.subheader("✍️ Enter Marks")
marks = {s: st.number_input(s, 0, 100) for s in subjects}

# ---------------- GENERATE ----------------
if st.button("📄 Generate Marksheet"):

    df = pd.DataFrame({
        "Subject": subjects,
        "Marks": marks.values()
    })
    df["Grade"] = df["Marks"].apply(grade)
    df["Result"] = df["Marks"].apply(lambda x: "PASS" if x >= 40 else "FAIL")

    total = df["Marks"].sum()
    avg = df["Marks"].mean()

    st.subheader("📊 Marksheet Preview")
    st.dataframe(df, use_container_width=True)

    st.success(f"Total: {total}")
    st.info(f"Average: {avg:.2f}%")

    # -------- CUT OFF --------
    if student_type=="School Student" and group=="Biology":
        eng = (marks["Maths"]+marks["Physics"]+marks["Chemistry"])/3
        med = (marks["Biology"]+marks["Physics"]+marks["Chemistry"])/3
        st.warning(f"Engineering Cutoff: {eng:.2f}")
        st.warning(f"Medical Cutoff: {med:.2f}")

    # -------- SUGGESTION --------
    if avg>=75:
        remark="Excellent performance"
    elif avg>=50:
        remark="Good, can improve"
    else:
        remark="Needs improvement"

    # -------- PDF GENERATION --------
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
                elems.append(Image(t.name,90,110))

        table_data=[["Subject","Marks","Grade","Result"]]+df.values.tolist()
        table=Table(table_data)
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.pink),
            ("GRID",(0,0),(-1,-1),1,colors.black)
        ]))
        elems.append(table)
        elems.append(Paragraph(f"<b>Teacher Remark:</b> {remark}", styles["Normal"]))
        doc.build(elems)
        return file

    pdf=build_pdf()

    with open(pdf,"rb") as f:
        st.download_button("⬇️ Download Marksheet PDF", f, "marksheet.pdf")

    # -------- EMAIL --------
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
