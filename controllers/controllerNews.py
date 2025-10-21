import datetime
import aiomysql
from db import get_db_connection


async def get_all_news():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM news WHERE status = 1")
        rows = await cursor.fetchall()
    conn.close()
    return rows


async def get_news_by_id(news_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM news WHERE id = %s", (news_id,))
        row = await cursor.fetchone()
    conn.close()
    return row


async def create_news(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # ✅ Validate foreign keys
        await cursor.execute("SELECT id FROM gallery WHERE id = %s", (data.get("image_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "image_id not found"}

        await cursor.execute("SELECT id FROM banner WHERE id = %s", (data.get("banner_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "banner_id not found"}

        await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "user_id not found"}

        now = datetime.datetime.now()
        insert_query = """
            INSERT INTO news (title, image_id, detail, banner_id, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("title"),
            data.get("image_id"),
            data.get("detail"),
            data.get("banner_id"),
            data.get("user_id"),
            data.get("status", 1),
            now,
            now
        )

        await cursor.execute(insert_query, values)
        news_id = cursor.lastrowid

    conn.close()
    return {"id": news_id, **data}


async def update_news(news_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # ✅ Check if news exists
        await cursor.execute("SELECT created_at FROM news WHERE id = %s", (news_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "News not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.now()

        update_query = """
            UPDATE news SET title=%s, image_id=%s, detail=%s, banner_id=%s,
            user_id=%s, status=%s, created_at=%s, updated_at=%s WHERE id=%s
        """
        values = (
            data.get("title"),
            data.get("image_id"),
            data.get("detail"),
            data.get("banner_id"),
            data.get("user_id"),
            data.get("status", 1),
            created_at,
            updated_at,
            news_id
        )

        await cursor.execute(update_query, values)

    conn.close()
    return {"id": news_id, **data, "created_at": created_at, "updated_at": updated_at}


async def delete_news(news_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("UPDATE news SET status = 0 WHERE id = %s", (news_id,))
    conn.close()
    return {"message": f"News {news_id} soft-deleted (status = 0)"}
