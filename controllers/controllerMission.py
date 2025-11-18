import os
import datetime
import aiomysql
from db import get_db_connection


# ---------------------------------------------------------------------
# 🔧 Fix image path by removing duplicated domain
# ---------------------------------------------------------------------
def build_url(path: str):
    """
    Fix path:
    - remove domain if already included
    - prepend CPANEL_BASE_URL
    """
    if not path:
        return None

    base = os.getenv("CPANEL_BASE_URL", "").rstrip("/")  # e.g. https://fujiairecambodia.com/uploads

    # Remove duplicate base URL
    if path.startswith(base):
        path = path.replace(base + "/", "").replace(base, "")

    path = path.lstrip("/")  # clean leading slash

    return f"{base}/{path}"


# ---------------------------------------------------------------------
# 🔧 Helper for all DB operations
# ---------------------------------------------------------------------
async def execute_query(query: str, params=None, fetchone=False, fetchall=False, commit=False):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, params or ())
            if commit:
                await conn.commit()
            if fetchone:
                return await cursor.fetchone()
            if fetchall:
                return await cursor.fetchall()
    finally:
        conn.close()


# ---------------------------------------------------------------------
# 🔹 Get all missions admin
# ---------------------------------------------------------------------
async def get_all_missions():
    missions = await execute_query(
        "SELECT * FROM mission ORDER BY id DESC",
        fetchall=True
    )

    # Fix image paths
    for m in missions:
        m["path"] = build_url(m.get("path"))

    return missions


# ---------------------------------------------------------------------
# 🔹 Get mission by id (public)
# ---------------------------------------------------------------------
async def get_mission_by_id(mission_id: int):
    mission = await execute_query(
        "SELECT * FROM mission WHERE id = %s AND status = 1",
        (mission_id,),
        fetchone=True
    )

    if mission:
        mission["path"] = build_url(mission.get("path"))

    return mission


# ---------------------------------------------------------------------
# 🔹 Create mission
# ---------------------------------------------------------------------
async def create_mission(data: dict):
    now = datetime.datetime.utcnow()

    query = """
        INSERT INTO mission (mission, value, history, image_id, path, user_id,
        status, created_at, updated_at)
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
        now,
    )

    conn = await get_db_connection()
    try:
        async with conn.cursor() as cursor:
            await cursor.execute(query, values)
            await conn.commit()
            mission_id = cursor.lastrowid
    finally:
        conn.close()

    data["path"] = build_url(data.get("path"))

    return {"id": mission_id, **data}


# ---------------------------------------------------------------------
# 🔹 Update mission
# ---------------------------------------------------------------------
async def update_mission(mission_id: int, data: dict):
    now = datetime.datetime.utcnow()

    query = """
        UPDATE mission
        SET mission=%s, value=%s, history=%s, image_id=%s, path=%s, user_id=%s,
        status=%s, updated_at=%s
        WHERE id=%s
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

    await execute_query(query, values, commit=True)

    data["path"] = build_url(data.get("path"))

    return {"id": mission_id, **data}


# ---------------------------------------------------------------------
# 🔹 Soft delete
# ---------------------------------------------------------------------
async def delete_mission(mission_id: int):
    await execute_query(
        "UPDATE mission SET status = 0 WHERE id = %s",
        (mission_id,),
        commit=True
    )
    return {"message": "Mission soft-deleted"}


# ---------------------------------------------------------------------
# 🔹 Public missions (clean paths)
# ---------------------------------------------------------------------
async def get_all_missions_public():
    missions = await execute_query(
        "SELECT * FROM mission WHERE status = 1",
        fetchall=True
    )

    for m in missions:
        m["path"] = build_url(m.get("path"))

    return missions
