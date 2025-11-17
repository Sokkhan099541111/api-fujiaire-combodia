import os
import datetime
import httpx
import aiosmtplib
from email.message import EmailMessage
from db import get_db_connection
from dotenv import load_dotenv

load_dotenv()

# Load mail config from env (updated names)
SMTP_HOST = os.getenv("MAIL_HOST")
SMTP_PORT = int(os.getenv("MAIL_PORT", 465))
SMTP_USERNAME = os.getenv("MAIL_USERNAME")
SMTP_PASSWORD = os.getenv("MAIL_PASSWORD")
SMTP_ENCRYPTION = os.getenv("MAIL_ENCRYPTION", "ssl").lower()

MAIL_FROM_ADDRESS = os.getenv("MAIL_FROM_ADDRESS", SMTP_USERNAME)
MAIL_FROM_NAME = os.getenv("MAIL_FROM_NAME", "No-Reply")

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
    await conn.commit()
    await conn.close()


async def send_email(name: str, email: str, subject: str, message: str):
    msg = EmailMessage()
    msg["From"] = f"{MAIL_FROM_NAME} <{MAIL_FROM_ADDRESS}>"
    msg["To"] = email
    msg["Subject"] = subject
    msg.set_content(f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}")

    # SSL or STARTTLS connection
    use_ssl = SMTP_ENCRYPTION == "ssl"

    await aiosmtplib.send(
        msg,
        hostname=SMTP_HOST,
        port=SMTP_PORT,
        username=SMTP_USERNAME,
        password=SMTP_PASSWORD,
        start_tls=not use_ssl,
        use_tls=use_ssl,
    )


async def send_telegram_message(name: str, email: str, subject: str, message: str):
    text = (
        f"New contact form submission:\n\n"
        f"Name: {name}\n"
        f"Email: {email}\n"
        f"Subject: {subject}\n"
        f"Message:\n{message}"
    )
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    async with httpx.AsyncClient() as client:
        await client.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": text})


async def submit_contact_controller(data: dict):
    name = data.get("name")
    email = data.get("email")
    subject = data.get("subject")
    message = data.get("message")

    # Basic validation
    if not all([name, email, subject, message]):
        return {"error": "All fields are required."}

    await save_to_database(name, email, subject, message)
    await send_email(name, email, subject, message)
    await send_telegram_message(name, email, subject, message)

    return {"message": "Contact form submitted successfully."}
# ✅ Include router for Contact Us