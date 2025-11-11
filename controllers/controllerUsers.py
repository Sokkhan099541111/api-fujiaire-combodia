import datetime
from fastapi import HTTPException
from security import hash_password, verify_password
from db import get_db_connection  # this should return an aiomysql connection
import aiomysql
import pymysql

# ===============================
# Users
# ===============================

async def get_all_users():
    conn = await get_db_connection()
    try:
        async with conn.cursor(aiomysql.DictCursor) as cursor:
            query = """
                SELECT 
                    u.id,
                    u.username,
                    u.email,
                    u.status,
                    u.created_at,
                    u.updated_at,
                    r.name AS role_name
                FROM users AS u
                LEFT JOIN roles AS r ON u.role_id = r.id
                ORDER BY u.id DESC
            """
            await cursor.execute(query)
            rows = await cursor.fetchall()
            return rows
    except Exception as e:
        print("❌ Error fetching users:", e)
        return []
    finally:
        conn.close()


async def get_user_by_id(user_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        user = await cursor.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def create_user(data: dict):
    now = datetime.datetime.now()
    hashed_pw = hash_password(data['password'])
    sql = """
        INSERT INTO users (username, password, email, role_id, status, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute(sql, (
            data['username'],
            hashed_pw,
            data['email'],
            data.get('role_id'),
            data.get('status', 1),
            now,
            now
        ))
        await conn.commit()
        new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id}

async def authenticate_user(email: str, password: str):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = await cursor.fetchone()
    conn.close()

    if not user or not verify_password(password, user['password']):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    return user

async def update_user(user_id: int, data: dict):
    now = datetime.datetime.now()
    sql = """
        UPDATE users
        SET username=%s, email=%s, role_id=%s, status=%s, updated_at=%s
        WHERE id = %s
    """
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute(sql, (
            data['username'],
            data.get('email'),
            data.get('role_id'),
            data.get('status', 1),
            now,
            user_id
        ))
        await conn.commit()
    conn.close()
    return {"message": "User updated successfully"}

async def delete_user(user_id: int):
    sql = "UPDATE users SET status = 0 WHERE id = %s"
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute(sql, (user_id,))
        await conn.commit()
    conn.close()
    return {"message": "User deactivated (status=0)"}

# ===============================
# Permissions
# ===============================

async def get_permissions_for_role(role_id: int):
    sql = """
        SELECT p.name
        FROM permissions p
        JOIN role_permissions rp ON p.id = rp.permission_id
        WHERE rp.role_id = %s
    """
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute(sql, (role_id,))
        perms = [row[0] for row in await cursor.fetchall()]
    conn.close()
    return perms

async def get_user_from_db(email: str):
    sql = """
        SELECT u.id, u.email, u.password, r.name AS role
        FROM users u
        JOIN role r ON u.role_id = r.id
        WHERE u.email = %s
    """
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(sql, (email,))
        user = await cursor.fetchone()
    conn.close()
    return user

async def get_user_permissions(user_id):
    sql_role = """
        SELECT p.name AS permission
        FROM permission p
        JOIN role_permission rp ON rp.permission_id = p.id
        JOIN users u ON u.role_id = rp.role_id
        WHERE u.id = %s
    """
    sql_user = """
        SELECT p.name AS permission
        FROM permission p
        JOIN user_permission up ON up.permission_id = p.id
        WHERE up.user_id = %s
    """
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute(sql_role, (user_id,))
            role_permissions = [row['permission'] for row in await cursor.fetchall()]

            await cursor.execute(sql_user, (user_id,))
            user_permissions = [row['permission'] for row in await cursor.fetchall()]
        except pymysql.err.ProgrammingError as e:
            # If table doesn't exist (errno 1146), return empty permissions instead of crashing
            if getattr(e, "args", [None])[0] == 1146:
                return []
            raise

    conn.close()
    return list(set(role_permissions + user_permissions))
