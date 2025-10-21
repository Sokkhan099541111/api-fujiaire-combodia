import datetime
import aiomysql
from db import get_db_connection


async def get_all_missions():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM mission WHERE status = 1")
        missions = await cursor.fetchall()
    conn.close()
    return missions


async def get_mission_by_id(mission_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM mission WHERE id = %s AND status = 1", (mission_id,))
        mission = await cursor.fetchone()
    conn.close()
    return mission


async def create_mission(data: dict):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        now = datetime.datetime.now()
        query = """
            INSERT INTO mission (mission, value, history, image_id, path, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (
            data.get("mission"),
            data.get("value"),
            data.get("history"),
            data.get("image_id"),
            data.get("path"),
            data.get("user_id"),
            data.get("status", 1),
            now,
            now
        )
        await cursor.execute(query, values)
        mission_id = cursor.lastrowid
    conn.close()
    return {"id": mission_id, **data}


async def update_mission(mission_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        now = datetime.datetime.now()
        query = """
            UPDATE mission SET mission=%s, value=%s, history=%s, image_id=%s,
            path=%s, user_id=%s, status=%s, updated_at=%s WHERE id=%s
        """
        values = (
            data.get("mission"),
            data.get("value"),
            data.get("history"),
            data.get("image_id"),
            data.get("path"),
            data.get("user_id"),
            data.get("status", 1),
            now,
            mission_id
        )
        await cursor.execute(query, values)
    conn.close()
    return {"id": mission_id, **data}


async def delete_mission(mission_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("UPDATE mission SET status = 0 WHERE id = %s", (mission_id,))
    conn.close()
    return {"message": "Mission soft-deleted"}


async def get_all_missions_public():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM mission WHERE status = 1")
        missions = await cursor.fetchall()
    conn.close()
    return missions
