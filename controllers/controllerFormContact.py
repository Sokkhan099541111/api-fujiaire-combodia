import datetime
import aiomysql
from db import get_db_connection

# -------------------------------------------------
# Get all form contact entries
# -------------------------------------------------
async def get_all_form_contacts():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM form_contact ORDER BY id DESC")
        rows = await cursor.fetchall()
    conn.close()
    return rows


# -------------------------------------------------
# Get single form contact by ID
# -------------------------------------------------
async def get_form_contact_by_id(contact_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM form_contact WHERE id = %s", (contact_id,))
        row = await cursor.fetchone()
    conn.close()
    return row


# -------------------------------------------------
# Create new form contact
# -------------------------------------------------
async def create_form_contact(data: dict):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        now = datetime.datetime.now()
        await cursor.execute("""
            INSERT INTO form_contact (title, name, subject, email, message, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            data.get("title"),
            data.get("name"),
            data.get("subject"),
            data.get("email"),
            data.get("message"),
            now
        ))
        await conn.commit()
        contact_id = cursor.lastrowid
    conn.close()
    return {"id": contact_id, **data, "created_at": now}


# -------------------------------------------------
# Update existing form contact
# -------------------------------------------------
async def update_form_contact(contact_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Preserve created_at
        await cursor.execute("SELECT created_at FROM form_contact WHERE id = %s", (contact_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Form contact not found"}

        created_at = row["created_at"]

        await cursor.execute("""
            UPDATE form_contact
            SET title = %s, name = %s, subject = %s, email = %s, message = %s, created_at = %s
            WHERE id = %s
        """, (
            data.get("title"),
            data.get("name"),
            data.get("subject"),
            data.get("email"),
            data.get("message"),
            created_at,
            contact_id
        ))
        await conn.commit()
    conn.close()
    return {"id": contact_id, **data, "created_at": created_at}


# -------------------------------------------------
# Delete a form contact
# -------------------------------------------------
async def delete_form_contact(contact_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("DELETE FROM form_contact WHERE id = %s", (contact_id,))
        await conn.commit()
    conn.close()
    return {"message": f"Form contact {contact_id} deleted"}
