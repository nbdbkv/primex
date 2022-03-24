from django.conf import settings
from django.core.mail import send_mail


def send_email(text):
    send_mail(
        "Feedback", text, settings.EMAIL_FROM, [settings.EMAIL_TO], fail_silently=True
    )
