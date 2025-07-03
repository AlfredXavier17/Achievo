from django.core.mail import send_mail
from django.urls import reverse

def send_verification_email(user, uidb64, token, domain):
    link = f"http://{domain}/verify-email/{uidb64}/{token}/"
    subject = "Verify your email for MilestoneMemo"
    message = f"Hi {user.email},\n\nPlease click the link below to verify your email:\n\n{link}\n\nIf you didn’t sign up, ignore this email."
    
    send_mail(
        subject,
        message,
        'Achievo <alfredxavierct@gmail.com>',
        [user.email],
        fail_silently=False,
    )
