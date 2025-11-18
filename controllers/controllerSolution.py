import os
import datetime
import aiomysql
from db import get_db_connection


# ===============================
# Helper: build full URL safely
# ===============================
def build_url(path: str):
    if not path:
        return None

    base = os.getenv("CPANEL_BASE_URL", "").rstrip("/")

    # Remove duplicated domain
    if path.startswith(base):
        path = path.replace(base, "").lstrip("/")

    path = path.lstrip("/")
    return f"{base}/{path}"


# ===============================
# Get all solutions (admin)
# ===============================
async def get_all_solutions():
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM solution ORDER BY id DESC")
            rows = await cursor.fetchall()

            # Add full URL
            for r in rows:
                r["path"] = build_url(r.get("path"))

        return rows
    finally:
        await conn.ensure_closed()


# ===============================
# Get solution by ID (admin)
# ===============================
async def get_solution_by_id(solution_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("SELECT * FROM solution WHERE id = %s", (solution_id,))
            row = await cursor.fetchone()

            if row:
                row["path"] = build_url(row.get("path"))

        return row
    finally:
        await conn.ensure_closed()


# ===============================
# Create solution
# ===============================
async def create_solution(data: dict):
    now = datetime.datetime.utcnow()

    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            # FK checks
            await cursor.execute("SELECT id FROM gallery WHERE id = %s", (data.get("image_id"),))
            if not await cursor.fetchone():
                return {"error": "image_id not found"}

            await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
            if not await cursor.fetchone():
                return {"error": "user_id not found"}

            await cursor.execute("""
                INSERT INTO solution
                (category, category_sub, title, image_id, path, user_id, status, created_at, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                data.get("category"),
                data.get("category_sub"),
                data.get("title"),
                data.get("image_id"),
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                now,
                now
            ))

            solution_id = cursor.lastrowid
            await conn.commit()

        data["path"] = build_url(data.get("path"))
        return {"id": solution_id, **data, "created_at": now, "updated_at": now}

    finally:
        await conn.ensure_closed()


# ===============================
# Update solution
# ===============================
async def update_solution(solution_id: int, data: dict):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:

            await cursor.execute("SELECT created_at FROM solution WHERE id=%s", (solution_id,))
            row = await cursor.fetchone()
            if not row:
                return {"error": "Solution not found"}

            created_at = row["created_at"]
            updated_at = datetime.datetime.utcnow()

            await cursor.execute("""
                UPDATE solution SET
                    category=%s,
                    category_sub=%s,
                    title=%s,
                    image_id=%s,
                    path=%s,
                    user_id=%s,
                    status=%s,
                    created_at=%s,
                    updated_at=%s
                WHERE id=%s
            """, (
                data.get("category"),
                data.get("category_sub"),
                data.get("title"),
                data.get("image_id"),
                data.get("path"),
                data.get("user_id"),
                data.get("status", 1),
                created_at,
                updated_at,
                solution_id
            ))

            await conn.commit()

        data["path"] = build_url(data.get("path"))

        return {
            "id": solution_id,
            **data,
            "created_at": created_at,
            "updated_at": updated_at
        }

    finally:
        await conn.ensure_closed()


# ===============================
# Soft delete solution
# ===============================
async def delete_solution(solution_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "UPDATE solution SET status = 0, updated_at=%s WHERE id=%s",
                (datetime.datetime.utcnow(), solution_id)
            )
            await conn.commit()

        return {"message": f"Solution {solution_id} soft-deleted"}

    finally:
        await conn.ensure_closed()


# ===============================
# Get solutions for public
# ===============================
async def get_all_solutions_public(limit: int = 4):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute("""
                SELECT * FROM solution
                WHERE status = 1
                ORDER BY id DESC
                LIMIT %s
            """, (limit,))
            rows = await cursor.fetchall()

            # Add full URL
            for r in rows:
                r["path"] = build_url(r.get("path"))

        return rows

    finally:
        await conn.ensure_closed()


# ===============================
# Get one public solution
# ===============================
async def get_solution_public_by_id(solution_id: int):
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(
                "SELECT * FROM solution WHERE id = %s AND status = 1",
                (solution_id,)
            )
            row = await cursor.fetchone()

            if row:
                row["path"] = build_url(row.get("path"))

        return row

    finally:
        await conn.ensure_closed()
