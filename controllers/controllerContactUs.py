import os
import datetime
import httpx
import aiosmtplib
from email.message import EmailMessage
from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


async def save_to_database(name: str, email: str, subject: str, message: str):
    conn = await get_db_connection()
    async with conn.cursor() as cur:
        created_at = updated_at = datetime.datetime.utcnow()
        await cur.execute(
            """
            INSERT INTO contact_us (name, email, subject, message, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (name, email, subject, message, created_at, updated_at),
        )
    conn.close()


async def send_email(name: str, email: str, subject: str, message: str):
    msg = EmailMessage()
    msg["From"] = SMTP_USERNAME
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        start_tls=True,
    )


async def send_telegram_message(name: str, email: str, subject: str, message: str):
    text = f"New contact form submission:\n\nName: {name}\nEmail: {email}\nSubject: {subject}\nMessage:\n{message}"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})


async def submit_contact_controller(data: dict):
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    # Validate (very basic)
    if not (name and email and subject and message):
        return {"error": "All fields are required."}

    await save_to_database(name, email, subject, message)
    await send_email(name, email, subject, message)
    await send_telegram_message(name, email, subject, message)

    return {"message": "Contact form submitted successfully."}
