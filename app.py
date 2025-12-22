import streamlit as st
import pandas as pd
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Image, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import tempfile
from twilio.rest import Client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Student Marksheet Portal", layout="wide")

# ---------------- GLOBAL STYLES ----------------
st.markdown("""
<style>
.stApp { background-color: #f4f6f8; }
.section-box {
    background: #ffffff;
    padding: 18px;
    border-radius: 8px;
    border: 1px solid #cccccc;
    margin-bottom: 16px;
}
</style>
""", unsafe_allow_html=True)

st.markdown("<h2 style='text-align:center;'>📘 Student Marksheet Portal</h2>", unsafe_allow_html=True)

# ---------------- FUNCTIONS ----------------
def get_grade(m):
    if m >= 90: return "O"
    elif m >= 80: return "A+"
    elif m >= 70: return "A"
    elif m >= 60: return "B"
    elif m >= 50: return "C"
    elif m >= 40: return "D"
    else: return "F"

def grade_point(grade):
    mapping = {"O":10,"A+":9,"A":8,"B":7,"C":6,"D":5,"F":0}
    return mapping.get(grade, 0)

def overall_result(fails):
    if fails == 0:
        return "🎉🙂 Excellent Performance"
    elif fails <= 2:
        return "⚠️😐 Needs Improvement"
    else:
        return "❌😞 Serious Improvement Required"

def teacher_remark(fails, avg):
    if fails == 0 and avg >= 75:
        return "🌟 Excellent academic performance. Keep it up!"
    elif fails == 0:
        return "Good effort. Performance can improve with consistency."
    elif fails <= 2:
        return "Needs improvement in weak subjects. Extra guidance recommended."
    else:
        return "Requires serious academic focus and regular mentoring."

# ---------------- TWILIO CONFIG ----------------
st.sidebar.header("📲 Twilio Settings")
twilio_sid = st.sidebar.text_input("ACf4037714656734c48983a372cae90430")
twilio_auth = st.sidebar.text_input("b575f2855eb25dc3a15fdc5145d517d6", type="password")
twilio_number = st.sidebar.text_input("+15707768661 (with +)")

# ---------------- INSTITUTE DETAILS ----------------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("🏫 Institute Details")
col_logo, col_name = st.columns([1, 5])
with col_logo:
    logo = st.file_uploader("Institute Logo", ["png", "jpg"])
    if logo:
        st.image(logo, width=90)
with col_name:
    inst_name = st.text_input("Institute Name")
    academic_year = st.text_input("Academic Year", "2024–2025")
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- STUDENT DETAILS ----------------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("👤 Student Details")
c1, c2, c3 = st.columns([2,2,1])
with c1:
    name = st.text_input("Student Name")
    reg_no = st.text_input("Register Number")
with c2:
    dob = st.date_input("Date of Birth")
    attendance = st.number_input("Attendance (%)", 0, 100, 75)
    parent_mobile = st.text_input("Parent Mobile (+CountryCode)")
with c3:
    photo = st.file_uploader("Student Photo", ["png", "jpg"])
    if photo:
        st.image(photo, width=90)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- SUBJECTS ----------------
subjects = ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"]
max_marks = 100
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.subheader("✍️ Marks Entry")
marks = {}
cols = st.columns(3)
for i, s in enumerate(subjects):
    with cols[i % 3]:
        marks[s] = st.number_input(s, 0, max_marks)
st.markdown('</div>', unsafe_allow_html=True)

# ---------------- GENERATE MARKSHEET ----------------
if st.button("📄 Generate Marksheet"):

    df = pd.DataFrame({
        "Subject": subjects,
        "Marks Obtained": marks.values(),
        "Max Marks": [max_marks]*len(subjects)
    })
    df["Grade"] = df["Marks Obtained"].apply(get_grade)
    df["Grade Point"] = df["Grade"].apply(grade_point)
    df["Result"] = df["Marks Obtained"].apply(lambda x: "PASS" if x >= 40 else "FAIL")

    total = df["Marks Obtained"].sum()
    total_max = df["Max Marks"].sum()
    avg = total / len(subjects)
    cgpa = df["Grade Point"].mean()
    fails = (df["Result"] == "FAIL").sum()
    overall = overall_result(fails)
    remark = teacher_remark(fails, avg)

    # ---------------- FRONTEND PREVIEW ----------------
    st.markdown('<div class="section-box">', unsafe_allow_html=True)
    st.subheader("📊 Marksheet Preview")
    st.dataframe(df.style.applymap(lambda val: "color: green" if val=="PASS" else "color: red", subset=["Result"]),
                 use_container_width=True)
    st.markdown(f"### 🎯 Overall Result: {overall}")
    st.markdown(f"**Average:** {avg:.2f}%")
    st.markdown(f"**CGPA:** {cgpa:.2f} / 10")
    st.markdown(f"**Teacher Remarks:** {remark}")
    st.markdown('</div>', unsafe_allow_html=True)

    # ---------------- PDF GENERATION ----------------
    def create_pdf():
        file_path = "marksheet.pdf"
        doc = SimpleDocTemplate(file_path, pagesize=A4)
        styles = getSampleStyleSheet()
        elements = []

        # Header
        header_table = []
        if logo:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(logo.read())
                img = Image(tmp.name, 60, 60)
                header_table.append([img, Paragraph(f"<b>{inst_name}</b>",
                    ParagraphStyle("h", alignment=TA_CENTER, fontSize=18, textColor=colors.darkblue))])
        else:
            header_table.append(["", Paragraph(f"<b>{inst_name}</b>",
                ParagraphStyle("h", alignment=TA_CENTER, fontSize=18, textColor=colors.darkblue))])
        ht = Table(header_table, colWidths=[70, 440])
        ht.setStyle(TableStyle([("VALIGN", (0,0), (-1,-1), "MIDDLE")]))
        elements.append(ht)
        elements.append(Spacer(1, 8))
        elements.append(Paragraph(f"<b>ANNUAL EXAMINATION – ACADEMIC YEAR {academic_year}</b>",
                                  ParagraphStyle("ay", alignment=TA_CENTER)))
        elements.append(Spacer(1, 14))

        # Student Info
        info_data = [
            ["Name", name, "DOB", str(dob)],
            ["Register No", reg_no, "Attendance", f"{attendance}%"],
            ["Parent Mobile", parent_mobile, "", ""]
        ]
        info_table = Table(info_data, colWidths=[90, 170, 90, 120])
        info_table.setStyle(TableStyle([("GRID", (0,0), (-1,-1), 1, colors.black)]))
        elements.append(info_table)

        if photo:
            with tempfile.NamedTemporaryFile(delete=False) as tmp:
                tmp.write(photo.read())
                img = Image(tmp.name, 80, 100)
                img.hAlign = "RIGHT"
                elements.append(img)

        elements.append(Spacer(1, 14))

        table_data = [df.columns.tolist()] + df.values.tolist()
        subject_table = Table(table_data, colWidths=[120, 80, 70, 60, 70, 60])
        subject_table.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 1, colors.black),
            ("BACKGROUND", (0,0), (-1,0), colors.lightgrey),
            ("ALIGN", (1,1), (-1,-1), "CENTER")
        ]))
        elements.append(subject_table)
        elements.append(Spacer(1, 12))

        summary = f"""
        <b>Total Marks:</b> {total}/{total_max}<br/>
        <b>Average:</b> {avg:.2f}%<br/>
        <b>CGPA:</b> {cgpa:.2f} / 10<br/>
        <b>Overall Result:</b> {overall}<br/><br/>
        <b>Teacher Remarks:</b> {remark}
        """
        elements.append(Paragraph(summary, styles["Normal"]))
        elements.append(Spacer(1, 30))

        footer = Table([["Class Teacher", "Parent", "Principal"]], colWidths=[170,170,170])
        footer.setStyle(TableStyle([
            ("LINEABOVE", (0,0), (-1,0), 1, colors.black),
            ("ALIGN", (0,0), (-1,-1), "CENTER")
        ]))
        elements.append(footer)

        doc.build(elements)
        return file_path

    pdf_file = create_pdf()
    with open(pdf_file, "rb") as f:
        st.download_button("⬇️ Download Marksheet PDF", f, "marksheet.pdf")

    # ---------------- SEND SMS ----------------
    if twilio_sid and twilio_auth and twilio_number and parent_mobile:
        try:
            client = Client(twilio_sid, twilio_auth)
            sms_body = f"🎓 {name}'s Marks:\n"
            for sub, mark in marks.items():
                sms_body += f"{sub}: {mark}\n"
            sms_body += f"Overall Result: {overall}\nRemark: {remark}"
            message = client.messages.create(
                body=sms_body,
                from_=twilio_number,
                to=parent_mobile
            )
            st.success(f"✅ SMS sent successfully! SID: {message.sid}")
        except Exception as e:
            st.error(f"❌ Failed to send SMS: {e}")
    else:
        st.warning("⚠️ Twilio settings or parent mobile number missing. SMS not sent.")
