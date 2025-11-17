import os
import httpx
import aiosmtplib
import datetime
from email.message import EmailMessage
from db import get_db_connection


# ------------------------------------
# Save to Database (with timestamps)
# ------------------------------------
async def save_to_database(name, email, message):
    created_at = datetime.datetime.utcnow()
    updated_at = datetime.datetime.utcnow()

    conn = await get_db_connection()
    async with conn.cursor() as cur:
        await cur.execute("""
            INSERT INTO contact (name, email, message, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (name, email, message, created_at, updated_at))
    conn.close()


# ------------------------------------
# Send to Telegram
# ------------------------------------
async def send_to_telegram(name, email, message):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    text = f"""
📩 NEW CONTACT
👤 Name: {name}
📧 Email: {email}

💬 Message:
{message}
"""

    async with httpx.AsyncClient() as client:
        await client.post(
            f"https://api.telegram.org/bot{token}/sendMessage",
            data={"chat_id": chat_id, "text": text}
        )


# ------------------------------------
# Send Email
# ------------------------------------
async def send_email(name, email, message):
    msg = EmailMessage()
    msg["Subject"] = "New Contact Message"
    msg["From"] = os.getenv("SMTP_USER")
    msg["To"] = os.getenv("SMTP_USER")

    msg.set_content(
        f"Name: {name}\nEmail: {email}\n\nMessage:\n{message}"
    )

    await aiosmtplib.send(
        msg,
        hostname=os.getenv("SMTP_HOST"),
        port=int(os.getenv("SMTP_PORT")),
        username=os.getenv("SMTP_USER"),
        password=os.getenv("SMTP_PASS"),
        start_tls=True
    )


# ------------------------------------
# Controller (JSON Body)
# ------------------------------------
async def submit_contact_controller(data: dict):
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    await save_to_database(name, email, message)
    await send_to_telegram(name, email, message)
    await send_email(name, email, message)

    return {"message": "Contact submitted successfully!"}
