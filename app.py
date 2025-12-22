from twilio.rest import Client

# Twilio credentials
account_sid = 'ACf4037714656734c48983a372cae90430'
auth_token = 'b575f2855eb25dc3a15fdc5145d517d6'
twilio_number = '+15707768661'  # Your Twilio phone number

# Initialize Twilio client
client = Client(account_sid, auth_token)

# Student and parent details
student_name = "Karthika"
parent_number = "+917639964635"  # Parent's phone number
marks = {
    "Maths": 95,
    "Science": 88,
    "English": 92
}

# Create marksheet message
marksheet_message = f"🎓 Marksheet for {student_name}:\n"
for subject, mark in marks.items():
    marksheet_message += f"{subject}: {mark}\n"

# Send SMS
try:
    message = client.messages.create(
        body=marksheet_message,
        from_=twilio_number,
        to=parent_number
    )
    print(f"✅ SMS sent successfully! SID: {message.sid}")
except Exception as e:
    print(f"❌ Failed to send SMS: {e}")
