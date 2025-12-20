# app.py
import streamlit as st
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Image, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import tempfile
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import base64
import os

# -------------------- PAGE CONFIG --------------------
st.set_page_config(
    page_title="Student Mark Generation Portal",
    page_icon="🎓",
    layout="wide"
)

# -------------------- HEADER --------------------
st.markdown("<h1 style='text-align:center;color:#1f4e79;'>🎓 Student Mark Generation Portal</h1>", unsafe_allow_html=True)

# -------------------- COLLECT STUDENT & PARENT DETAILS --------------------
with st.expander("Enter Student Details"):
    school_name = st.text_input("School / College Name")
    student_name = st.text_input("Student Name")
    register_no = st.text_input("Register Number")
    dob = st.date_input("Date of Birth")
    father_name = st.text_input("Father Name")
    mother_name = st.text_input("Mother Name")
    attendance = st.number_input("Attendance Percentage", 0, 100)
    photo = st.file_uploader("Upload Student Photo", type=["png","jpg","jpeg"])
    
with st.expander("Enter Parent Contact Details"):
    parent_email = st.text_input("Parent Email")
    parent_mobile = st.text_input("Parent Mobile Number")

# -------------------- STUDENT TYPE --------------------
student_type = st.selectbox("Select Student Type", ["School Student", "College Student"])

# -------------------- SCHOOL STUDENT MODULE --------------------
if student_type == "School Student":
    group = st.selectbox("Select Group", ["Biology", "Computer Science", "Commerce", "History"])
    subjects_dict = {
        "Biology": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Biology"],
        "Computer Science": ["Tamil", "English", "Maths", "Physics", "Chemistry", "Computer Science"],
        "Commerce": ["Tamil", "English", "Accountancy", "Economics", "Commerce", "Maths"],
        "History": ["Tamil", "English", "History", "Civics", "Geography", "Economics"]
    }
    subjects = subjects_dict[group]
    marks = {}
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100)

# -------------------- COLLEGE STUDENT MODULE --------------------
if student_type == "College Student":
    department = st.selectbox("Select Department", ["CSE","ECE","Biotechnology"])
    semester = st.selectbox("Select Semester", [f"SEM {i}" for i in range(1,9)])
    college_subjects = {
        "CSE": ["DS","OS","DBMS","Python","Java","Networking"],
        "ECE": ["Signals","Electronics","Microprocessor","Communications","Mathematics","Physics"],
        "Biotechnology": ["Genetics","Biochemistry","Microbiology","Cell Biology","Chemistry","Physics"]
    }
    subjects = college_subjects[department]
    marks = {}
    for sub in subjects:
        marks[sub] = st.number_input(f"{sub} Marks", 0, 100)

# -------------------- GRADE LOGIC --------------------
def grade(mark):
    if mark >=90: return "A+", colors.green, "Pass"
    elif mark >=80: return "A", colors.green, "Pass"
    elif mark >=70: return "B+", colors.green, "Pass"
    elif mark >=60: return "B", colors.green, "Pass"
    elif mark >=50: return "C", colors.yellow, "Pass"
    else: return "D", colors.red, "Fail"

# -------------------- GENERATE MARKSHEET --------------------
if st.button("Generate Marksheet & PDF"):
    total = sum(marks.values())
    average = total / len(marks)
    
    # -------------------- DISPLAY MARKS TABLE --------------------
    table_display = [["Subject","Marks","Grade","Pass/Fail"]]
    for sub in subjects:
        g, c, status = grade(marks[sub])
        table_display.append([sub, marks[sub], g, status])
    st.table(table_display)
    
    # -------------------- CREATE PDF --------------------
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
        pdf_path = tmp_pdf.name
    
    doc = SimpleDocTemplate(pdf_path, pagesize=A4)
    elements = []
    styles = getSampleStyleSheet()
    
    # School/College Name
    elements.append(Paragraph(f"<b>{school_name}</b>", styles['Title']))
    elements.append(Spacer(1,12))
    
    # Photo
    if photo:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
            tmp_img.write(photo.getvalue())
            tmp_img_path = tmp_img.name
        img = Image(tmp_img_path, width=100, height=100)
        elements.append(img)
    
    # Student Details
    student_info = f"""
    Name: {student_name}<br/>
    Register No: {register_no}<br/>
    DOB: {dob}<br/>
    Father: {father_name}<br/>
    Mother: {mother_name}<br/>
    Attendance: {attendance}%
    """
    elements.append(Paragraph(student_info, styles['Normal']))
    elements.append(Spacer(1,12))
    
    # Annual Exam Result heading
    elements.append(Paragraph("<b>ANNUAL EXAMINATION RESULT</b>", styles['Heading2']))
    elements.append(Spacer(1,12))
    
    # Table Data
    data = [["Subject","Marks","Grade","Pass/Fail"]]
    for sub in subjects:
        g, c, status = grade(marks[sub])
        data.append([sub, str(marks[sub]), g, status])
    
    table = Table(data, colWidths=[120,50,50,50])
    style = TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightblue),
        ('TEXTCOLOR',(0,0),(-1,0),colors.white),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('GRID',(0,0),(-1,-1),1,colors.black)
    ])
    # Row coloring based on pass/fail
    for i,row in enumerate(data[1:], start=1):
        if row[3]=="Fail":
            style.add('BACKGROUND',(0,i),(-1,i),colors.red)
        else:
            style.add('BACKGROUND',(0,i),(-1,i),colors.green)
    table.setStyle(style)
    elements.append(table)
    
    # Totals
    elements.append(Spacer(1,12))
    elements.append(Paragraph(f"<b>Total Marks:</b> {total}    <b>Average:</b> {average:.2f}", styles['Normal']))
    
    # Cutoffs for school students
    if student_type=="School Student":
        if group=="Biology":
            med_cutoff = marks["Biology"] + (marks["Physics"] + marks["Chemistry"])/2
            elements.append(Paragraph(f"<b>Medical Cutoff:</b> {med_cutoff}", styles['Normal']))
        if group in ["Biology","Computer Science"]:
            eng_cutoff = marks.get("Maths",0)+(marks.get("Physics",0)+marks.get("Chemistry",0))/2
            elements.append(Paragraph(f"<b>Engineering Cutoff:</b> {eng_cutoff}", styles['Normal']))
    
    doc.build(elements)
    st.success("✅ PDF Generated Successfully!")
    
    # -------------------- DOWNLOAD BUTTON --------------------
    with open(pdf_path,"rb") as f:
        pdf_data = f.read()
    st.download_button("📥 Download PDF", data=pdf_data, file_name=f"{student_name}_marksheet.pdf", mime="application/pdf")
    
    # -------------------- SEND EMAIL VIA SENDGRID --------------------
    send_email = st.checkbox("Send Marksheet to Parent Email")
    if send_email and parent_email:
        sg_api_key = os.environ.get("SENDGRID_API_KEY")
        if not sg_api_key:
            st.error("SendGrid API Key not found in environment variables.")
        else:
            try:
                message = Mail(
                    from_email="school_verified_email@example.com",
                    to_emails=parent_email,
                    subject="Your Child's Marksheet",
                    html_content=f"<p>Dear Parent,<br>Please find attached the marksheet of {student_name}.</p>"
                )
                encoded_file = base64.b64encode(pdf_data).decode()
                attachedFile = Attachment(
                    FileContent(encoded_file),
                    FileName(f"{student_name}_marksheet.pdf"),
                    FileType("application/pdf"),
                    Disposition("attachment")
                )
                message.attachment = attachedFile
                sg = SendGridAPIClient(sg_api_key)
                response = sg.send(message)
                st.success(f"✅ Email sent to {parent_email}")
            except Exception as e:
                st.error(f"Error sending email: {e}")
