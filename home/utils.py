from django.core.mail import EmailMessage
from twilio.rest import Client
from django.conf import settings
import os

def send_otp_via_sms(mobile, otp):
    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        message = client.messages.create(
            body=f"Your Otp is: {otp}\nFrom Khana Khajana",
            from_=settings.TWILIO_PHONE_NUMBER,
            to=f"+91{mobile}"  
        )
        return message.sid
    except Exception as e:
        print(f"Error sending SMS: {e}")
        return None


class Util:
     @staticmethod
     def send_email(data):
          email = EmailMessage(
               subject=data['subject'],
               body=data['body'],
               from_email=os.environ.get('EMAIL_FROM'),
               to=[data['to_email']]
          )
          email.send()