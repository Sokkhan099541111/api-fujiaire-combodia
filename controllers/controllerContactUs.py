import aiomysql
import httpx
import aiosmtplib
from email.message import EmailMessage
from datetime import datetime
from db import get_db_connection


# ----------------------------
# SAVE TO DATABASE
# ----------------------------
async def save_to_database(name, email, subject, message):
    created_at = datetime.utcnow()
    updated_at = datetime.utcnow()

    conn = await get_db_connection()
    async with conn.cursor() as cur:
        await cur.execute("""
            INSERT INTO contact_us (name, email, subject, message, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (name, email, subject, message, created_at, updated_at))

        await conn.commit()


# ----------------------------
# SEND TELEGRAM
# ----------------------------
async def send_to_telegram(name, email, subject, message):
    TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
    CHAT_ID = "YOUR_CHAT_ID"

    text = (
        f"📩 *New Contact Message*\n\n"
        f"👤 Name: {name}\n"
        f"📧 Email: {email}\n"
        f"📝 Subject: {subject}\n"
        f"💬 Message:\n{message}\n"
    )

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text, "parse_mode": "Markdown"}

    async with httpx.AsyncClient() as client:
        await client.post(url, json=payload)


# ----------------------------
# SEND EMAIL
# ----------------------------
async def send_email(name, email, subject, message):
    msg = EmailMessage()
    msg["From"] = "YOUR_EMAIL@gmail.com"
    msg["To"] = "YOUR_EMAIL@gmail.com"
    msg["Subject"] = f"New Contact Message: {subject}"

    msg.set_content(
        f"""
New Contact Form Submission

Name: {name}
Email: {email}
Subject: {subject}

Message:
{message}
"""
    )

    await aiosmtplib.send(
        msg,
        hostname="smtp.gmail.com",
        port=587,
        username="YOUR_EMAIL@gmail.com",
        password="YOUR_APP_PASSWORD",
        start_tls=True,
    )


# ----------------------------
# MAIN CONTROLLER
# ----------------------------
async def submit_contact_controller(data: dict):
    name = data.get("name", "")
    email = data.get("email", "")
    subject = data.get("subject", "") or ""   # FIX: never NULL
    message = data.get("message", "")

    # Save to DB
    await save_to_database(name, email, subject, message)

    # Send Telegram
    await send_to_telegram(name, email, subject, message)

    # Send Email
    await send_email(name, email, subject, message)

    return {"status": "success", "message": "Contact submitted successfully"}
