import smtplib
from email.message import EmailMessage
from scheduler import scheduler
from datetime import datetime, timedelta

SENDER_EMAIL = 'kleckovkinaa@yandex.ru'
SENDER_PASSWORD = 'suslnpqvbmqtvvto'
SMTP_SERVER = 'smtp.yandex.ru'
SMTP_PORT = 587

def send_email(to_email, subject, body):
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.set_content(body)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.send_message(msg)

def send_confirmation_email(email, name):
    subject = 'Вы успешно записались на вебинар'
    body = f'Привет, {name}!\n\nВы успешно записались. Мы пришлём ссылку позже.'
    send_email(email, subject, body)

def schedule_webinar_email(email, name):
    webinar_time = datetime.now() + timedelta(minutes=1)
    scheduler.add_job(
        send_webinar_email,
        'date',
        run_date=webinar_time,
        args=[email, name]
    )

def send_webinar_email(email, name):
    subject = 'Ссылка на вебинар'
    body = f'Привет, {name}!\n\nВот ссылка на вебинар: https://example.com/webinar'
    send_email(email, subject, body)
