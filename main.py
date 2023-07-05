import logging
import os
from dotenv import load_dotenv
import smtplib

from email_validator import EmailNotValidError, validate_email
from email.mime.text import MIMEText

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel
import pytest


load_dotenv()


def create_app():
    app = FastAPI(title='Mailer', debug=False)
    return app


app = create_app()
logging.basicConfig(filename='email_logs.log', level=logging.INFO)


class Email(BaseModel):
    to: str
    subject: str
    message: str


@app.post('/send_email')
def send_email(mail: Email):

    sender = 'makiellstore@gmail.com'
    password = os.getenv("EMAIL_APP_PASSWORD")

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    try:

        server.login(sender, password)
        v = validate_email(mail.to)
        to = v.normalized
        msg = MIMEText(mail.subject)
        server.sendmail(sender, to, msg.as_string())

        logging.info(f"Email sent to: {mail.to}, Subject: {mail.subject}, Message: {mail.message}")
        
        return {"message": "Email sent successfully"}

    except EmailNotValidError as e:

        logging.error(f"Email wasn't sent to: {mail.to}, Error: {e}")
        return str(e)


@pytest.fixture(scope="module")
def test_app():
    return TestClient(app)


def test_send_email(test_app):

    email_data = {
        "to": "recipient@gmail.com",
        "subject": "Test email",
        "message": "This is a test email."
    }

    response = test_app.post("/send_email", json=email_data)

    assert response.status_code == 200
    assert response.json() == {"message": "Email sent successfully"}
