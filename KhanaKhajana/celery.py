import os
from celery import Celery
from django.core.mail import send_mail
from home.utils import send_otp_via_sms

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'KhanaKhajana.settings')

app = Celery('KhanaKhajana')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.task
def send_driver_email(subject, message, sender, reciever):
    send_mail(subject, message, from_email=sender,recipient_list=reciever)

@app.task
def send_otp_sms_async(mobile_number, otp):
    return send_otp_via_sms(mobile_number, otp)