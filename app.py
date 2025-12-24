from twilio.rest import Client

# Twilio credentials
account_sid = "YOUR_ACCOUNT_SID"
auth_token = "YOUR_AUTH_TOKEN"
twilio_number = "+15707768661"

client = Client(account_sid, auth_token)

parent_number = "+917639964635"

message_text = (
    "Dear Karuppasamy, "
    "This message is sent with concern for your child’s well-being. "
    "She is under emotional stress and needs understanding and support at this time. "
    "Please consider speaking calmly and seeking guidance from trusted family members "
    "or professional counselors. Support and care can make a big difference."
)

try:
    message = client.messages.create(
        body=message_text,
        from_=twilio_number,
        to=parent_number
    )
    print("✅ Message sent successfully")
except Exception as e:
    print("❌ Failed to send SMS:", e)
