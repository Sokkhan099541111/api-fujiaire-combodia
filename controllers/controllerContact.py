import aiomysql
from db import get_db_connection

# ----------------------------------------
# Get all contact records
# ----------------------------------------
async def get_all_contacts():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM contact_us")
        rows = await cursor.fetchall()
    conn.close()
    return rows

# ----------------------------------------
# Get contact by ID
# ----------------------------------------
async def get_contact_by_id(contact_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM contact_us WHERE id = %s", (contact_id,))
        row = await cursor.fetchone()
    conn.close()
    return row

# ----------------------------------------
# Create a new contact record
# ----------------------------------------
async def create_contact(data: dict):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("""
            INSERT INTO contact_us (title, email, telegram, facebook, instagram, tiktok, youtube, address)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("title"),
            data.get("email"),
            data.get("telegram"),
            data.get("facebook"),
            data.get("instagram"),
            data.get("tiktok"),
            data.get("youtube"),
            data.get("address"),
        ))
        await conn.commit()
        contact_id = cursor.lastrowid
    conn.close()
    return {"id": contact_id, **data}

# ----------------------------------------
# Update contact by ID
# ----------------------------------------
async def update_contact(contact_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("""
            UPDATE contact_us SET
            title = %s, email = %s, telegram = %s, facebook = %s,
            instagram = %s, tiktok = %s, youtube = %s, address = %s
            WHERE id = %s
        """, (
            data.get("title"),
            data.get("email"),
            data.get("telegram"),
            data.get("facebook"),
            data.get("instagram"),
            data.get("tiktok"),
            data.get("youtube"),
            data.get("address"),
            contact_id
        ))
        await conn.commit()
    conn.close()
    return {"id": contact_id, **data}

# ----------------------------------------
# Delete contact by ID
# ----------------------------------------
async def delete_contact(contact_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("DELETE FROM contact_us WHERE id = %s", (contact_id,))
        await conn.commit()
    conn.close()
    return {"message": f"Contact {contact_id} deleted"}
