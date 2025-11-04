import datetime
from db import get_db_connection  # Your existing sync MySQL connection

# -------------------------
# Fetch all industries
# -------------------------
def get_all_industries():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM industry_development")
    rows = cursor.fetchall()
    conn.close()
    return rows

# -------------------------
# Fetch industry by ID
# -------------------------
def get_industry_by_id(industry_id: int):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM industry_development WHERE id=%s", (industry_id,))
    row = cursor.fetchone()
    conn.close()
    return row

# -------------------------
# Create industry
# -------------------------
def create_industry(data: dict):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check FK image_id
    cursor.execute("SELECT id FROM gallery WHERE id=%s", (data.get("image_id"),))
    if not cursor.fetchone():
        conn.close()
        return {"error": "image_id not found"}

    # Check FK user_id
    cursor.execute("SELECT id FROM users WHERE id=%s", (data.get("user_id"),))
    if not cursor.fetchone():
        conn.close()
        return {"error": "user_id not found"}

    now = datetime.datetime.now()
    cursor.execute("""
        INSERT INTO industry_development
            (year, title, image_id, path, user_id, status, created_at, updated_at)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, (
        data.get("year"),
        data.get("title"),
        data.get("image_id"),
        data.get("path"),
        data.get("user_id"),
        data.get("status", 1),
        now,
        now
    ))
    conn.commit()
    industry_id = cursor.lastrowid
    conn.close()
    return {"id": industry_id, **data}

# -------------------------
# Update industry
# -------------------------
def update_industry(industry_id: int, data: dict):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT created_at FROM industry_development WHERE id=%s", (industry_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return {"error": "Industry development not found"}

    created_at = row["created_at"]
    updated_at = datetime.datetime.now()

    cursor.execute("""
        UPDATE industry_development
        SET year=%s, title=%s, image_id=%s, path=%s, user_id=%s, status=%s,
            created_at=%s, updated_at=%s
        WHERE id=%s
    """, (
        data.get("year"),
        data.get("title"),
        data.get("image_id"),
        data.get("path"),
        data.get("user_id"),
        data.get("status", 1),
        created_at,
        updated_at,
        industry_id
    ))
    conn.commit()
    conn.close()
    return {"id": industry_id, **data, "created_at": created_at, "updated_at": updated_at}

# -------------------------
# Soft delete industry
# -------------------------
def delete_industry(industry_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE industry_development SET status=0 WHERE id=%s", (industry_id,))
    conn.commit()
    conn.close()
    return {"message": f"Industry development {industry_id} soft-deleted"}

# -------------------------
# Public fetch all industries
# -------------------------
def get_all_industries_public():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM industry_development WHERE status=1")
    rows = cursor.fetchall()
    conn.close()
    return rows
