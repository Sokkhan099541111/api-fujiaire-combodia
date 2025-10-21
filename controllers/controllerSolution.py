import datetime
import aiomysql
from db import get_db_connection  # returns aiomysql.Connection

# ===============================
# Get all solutions (admin)
# ===============================
async def get_all_solutions():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM solution WHERE status = 1")
        rows = await cursor.fetchall()
    conn.close()
    return rows

# ===============================
# Get solution by ID (admin)
# ===============================
async def get_solution_by_id(solution_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM solution WHERE id = %s", (solution_id,))
        row = await cursor.fetchone()
    conn.close()
    return row

# ===============================
# Create solution
# ===============================
async def create_solution(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Validate foreign keys
        await cursor.execute("SELECT id FROM gallery WHERE id = %s", (data.get("image_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "image_id not found"}

        await cursor.execute("SELECT id FROM users WHERE id = %s", (data.get("user_id"),))
        if not await cursor.fetchone():
            conn.close()
            return {"error": "user_id not found"}

        now = datetime.datetime.now()
        await cursor.execute("""
            INSERT INTO solution (category, category_sub, title, image_id, path, user_id, status, created_at, updated_at)
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
    conn.close()
    return {"id": solution_id, **data}

# ===============================
# Update solution
# ===============================
async def update_solution(solution_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT created_at FROM solution WHERE id = %s", (solution_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Solution not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.now()

        await cursor.execute("""
            UPDATE solution SET
                category = %s,
                category_sub = %s,
                title = %s,
                image_id = %s,
                path = %s,
                user_id = %s,
                status = %s,
                created_at = %s,
                updated_at = %s
            WHERE id = %s
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
    conn.close()
    return {"id": solution_id, **data}

# ===============================
# Soft delete solution
# ===============================
async def delete_solution(solution_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("UPDATE solution SET status = 0 WHERE id = %s", (solution_id,))
        await conn.commit()
    conn.close()
    return {"message": f"Solution {solution_id} soft-deleted"}

# ===============================
# Get solutions for public
# ===============================
async def get_all_solutions_public(limit: int = 4):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("""
            SELECT * FROM solution
            WHERE status = 1
            ORDER BY id DESC
            LIMIT %s
        """, (limit,))
        rows = await cursor.fetchall()
    conn.close()
    return rows

async def get_solution_public_by_id(solution_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM solution WHERE id = %s AND status = 1", (solution_id,))
        row = await cursor.fetchone()
    conn.close()
    return row
