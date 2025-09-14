from twilio.rest import Client
import os

import dotenv
dotenv.load_dotenv()

client = Client(os.getenv("ACCOUNT_SID"), os.getenv("AUTH_TOKEN"))

message = "hi"

message_obj = client.messages.create(
    from_='whatsapp:+14155238886',
    body=message,
    to='whatsapp:+6588663319'
)