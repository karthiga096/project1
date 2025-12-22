import streamlit as st
from twilio.rest import Client

# ------------------ TWILIO CONFIG ------------------
ACCOUNT_SID = "ACf4037714656734c48983a372cae90430"
AUTH_TOKEN = "0d39eef3e8c7d19c2b91a4f25c071df5"
TWILIO_NUMBER = "+15707768661"   # Your Twilio phone number

# ------------------ SMS FUNCTION ------------------
def send_sms(parent_mobile, student_name, marks):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)

    total = 0
    message = f"📘 MARKSHEET\nStudent: {student_name}\n\n"

    for subject, mark in marks.items():
        message += f"{subject}: {mark}\n"
        total += mark

    result = "PASS" if total >= 150 else "FAIL"

    message += f"\nTotal: {total}\nResult: {result}\n\n- School Management"

    client.messages.create(
        body=message,
        from_=TWILIO_NUMBER,
        to=parent_mobile
    )

# ------------------ STREAMLIT UI ------------------
st.set_page_config(page_title="Student Marksheet SMS", page_icon="📘")
st.title("🎓 Student Marksheet SMS System")

st.subheader("Student Details")
student_name = st.text_input("Student Name")
parent_mobile = st.text_input("Parent Mobile Number (+91...)")

st.subheader("Enter Marks")
maths = st.number_input("Maths", 0, 100)
science = st.number_input("Science", 0, 100)
english = st.number_input("English", 0, 100)

if st.button("📲 Send Marksheet SMS"):
    if student_name == "" or parent_mobile == "":
        st.error("Please fill all details")
    else:
        marks = {
            "Maths": maths,
            "Science": science,
            "English": english
        }

        try:
            send_sms(parent_mobile, student_name, marks)
            st.success("✅ Marksheet SMS sent to parent successfully!")
        except Exception as e:
            st.error("❌ Failed to send SMS")
            st.write(e)
