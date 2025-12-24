import streamlit as st
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Parent SMS Alert", layout="centered")
st.title("📩 Parent SMS Alert System")

# ---------------- TWILIO CREDENTIALS ----------------
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
        "Dear Karuppasamy, this message is sent with concern for your child’s well-being. "
        "She is under emotional stress and needs care, understanding, and support. "
        "Please consider speaking calmly and seeking guidance."
    ),
    height=150
)

# ---------------- SEND SMS ----------------
if st.button("📨 Send SMS"):
    if not parent_number or not message_text:
        st.warning("⚠️ Please fill all fields")
    else:
        try:
            # Attempt to send SMS
            message = client.messages.create(
                body=message_text,
                from_=TWILIO_NUMBER,
                to=parent_number
            )
            st.success("✅ SMS sent successfully!")
            st.write("Message SID:", message.sid)

        except TwilioRestException as e:
            # Handle Trial account unverified number error
            if e.code == 21614:
                st.error(
                    "❌ Cannot send SMS: This number is unverified in your Twilio trial account. "
                    "Please verify it here: https://www.twilio.com/console/phone-numbers/verified"
                )
            else:
                st.error(f"❌ Failed to send SMS: {e.msg}")
