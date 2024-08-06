import random
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from cuentas.models import User

import threading


class EmailThread(threading.Thread):

    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.email.send()


class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data['email_subject'], body=data['email_body'], to=[data['to_email']])
        EmailThread(email).start()


    def  email_otp_verifcation(email):
            subject='OTP For  Email Verification'
            otp=random.randint(1,100)
            message=f'your otp is {otp}'
            email_from='tup@gmail.com'
            send_mail(subject,message,email_from,[email])
            user_obj=User.objects.get(email=email)
            user_obj.otp=otp
            user_obj.save()
        
    def  password_reset_otp(email):
            subject='OTP For  Password Reset'
            otp=random.randint(100000,999999)
            message=f'your otp is {otp}'
            email_from='tup@gmail.com'
            send_mail(subject,message,email_from,[email])
            user_obj=User.objects.get(email=email)
            user_obj.otp=otp
            user_obj.save()
        