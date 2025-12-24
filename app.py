import streamlit as st
from twilio.rest import Client

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Parent SMS Alert", layout="centered")

st.title("📩 Parent SMS Alert System")

# ---------------- TWILIO CREDENTIALS ----------------
# ⚠️ Replace with your REAL Twilio details
ACCOUNT_SID = "ACf4037714656734c48983a372cae90430"
AUTH_TOKEN = "6954e01962a6595dd20b6baf654d55e0"
TWILIO_NUMBER = "+15707768661"   # Your Twilio number

client = Client(ACCOUNT_SID, AUTH_TOKEN)

# ---------------- INPUTS ----------------
parent_number = st.text_input(
    "Parent Mobile Number",
    placeholder="+91XXXXXXXXXX"
)

message_text = st.text_area(
    "Message to Parent",
    value=(
        "Dear Karuppasamy, "
        "this message is sent with concern for your child’s well-being. "
        "She is under emotional stress and needs care, understanding, "
        "and support. Please consider speaking calmly and seeking guidance."
    ),
    height=150
)

# ---------------- SEND SMS ----------------
if st.button("📨 Send SMS"):
    if parent_number == "" or message_text == "":
        st.warning("⚠️ Please fill all fields")
    else:
        try:
            message = client.messages.create(
                body=message_text,
                from_=TWILIO_NUMBER,
                to=parent_number
            )
            st.success("✅ SMS sent successfully!")
            st.write("Message SID:", message.sid)

        except Exception as e:
            st.error("❌ Failed to send SMS")
            st.write(e)
