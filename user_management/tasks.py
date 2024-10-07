from django.core.mail import send_mail
from crudproject.celery import app


@app.task
def add(x, y):
    return x + y


@app.task
def send_welcome_email(from_email, to_email, subject, message):
    try:
        send_mail(
            subject,
            message,
            from_email,
            [to_email],
            fail_silently=False,
        )
    except Exception as e:
        print(f"Error sending email to {to_email}: {str(e)}")
