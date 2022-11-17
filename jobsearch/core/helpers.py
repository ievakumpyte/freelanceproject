from django.core.mail import send_mail

from django.conf import settings
import uuid

def send_forget_password_email(email, token):

    token = str(uuid.uuid4())
    subject = 'Slaptažodžio pakeitimo nuoroda'
    message = f' Norėdami pakeisti slaptažodį, paspauskite ant nuorodos'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [email]
    send_mail(subject,message,email_from, recipient_list)
    return True