import datetime
import aiomysql
from db import get_db_connection


# ✅ Get all categories (admin)
async def get_all_categories():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM category WHERE status = 1")
        categories = await cursor.fetchall()

        # Fetch related images for each category
        for category in categories:
            await cursor.execute(
                "SELECT id, image_id, path FROM category_images WHERE category_id = %s",
                (category["id"],)
            )
            category["images"] = await cursor.fetchall()

    conn.close()
    return categories


# ✅ Get category by ID
async def get_category_by_id(category_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM category WHERE id = %s", (category_id,))
        category = await cursor.fetchone()

        if category:
            await cursor.execute(
                "SELECT id, image_id, path FROM category_images WHERE category_id = %s",
                (category_id,)
            )
            category["images"] = await cursor.fetchall()
        else:
            category = None

    conn.close()
    return category


# ✅ Create a new category
async def create_category(data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        now = datetime.datetime.now()

        images = data.get("images", [])
        first_image = images[0] if images else None

        # Insert into main category table
        await cursor.execute("""
            INSERT INTO category
                (name, image_id, path, discriptions, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data.get("name"),
            first_image["id"] if first_image else None,
            first_image["path"] if first_image else None,
            data.get("discriptions"),
            data.get("user_id"),
            data.get("status", 1),
            now,
            now
        ))
        category_id = cursor.lastrowid

        # Insert multiple images
        for img in images:
            await cursor.execute("""
                INSERT INTO category_images (category_id, image_id, path, created_at)
                VALUES (%s, %s, %s, %s)
            """, (
                category_id,
                img.get("id"),
                img.get("path"),
                now
            ))

        await conn.commit()

    conn.close()
    return {
        "id": category_id,
        "name": data.get("name"),
        "image_id": first_image["id"] if first_image else None,
        "path": first_image["path"] if first_image else None,
        "discriptions": data.get("discriptions"),
        "status": data.get("status", 1),
        "user_id": data.get("user_id"),
        "images": images
    }


# ✅ Update category
async def update_category(category_id: int, data: dict):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Preserve created_at
        await cursor.execute("SELECT created_at FROM category WHERE id = %s", (category_id,))
        row = await cursor.fetchone()
        if not row:
            conn.close()
            return {"error": "Category not found"}

        created_at = row["created_at"]
        updated_at = datetime.datetime.now()

        # Update main category
        await cursor.execute("""
            UPDATE category
            SET name = %s, image_id = %s, path = %s, user_id = %s,
                discriptions = %s, status = %s, created_at = %s, updated_at = %s
            WHERE id = %s
        """, (
            data.get("name"),
            data.get("image_id"),
            data.get("path"),
            data.get("user_id"),
            data.get("discriptions"),
            data.get("status", 1),
            created_at,
            updated_at,
            category_id
        ))

        # Manage multi-images
        if "images" in data:
            await cursor.execute("DELETE FROM category_images WHERE category_id = %s", (category_id,))
            for img in data["images"]:
                await cursor.execute("""
                    INSERT INTO category_images (category_id, image_id, path, created_at)
                    VALUES (%s, %s, %s, %s)
                """, (
                    category_id,
                    img.get("id"),
                    img.get("path"),
                    created_at
                ))

        await conn.commit()

    conn.close()
    return {
        "id": category_id,
        **data,
        "created_at": created_at,
        "updated_at": updated_at
    }


# ✅ Soft delete category
async def delete_category(category_id: int):
    conn = await get_db_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("UPDATE category SET status = 0 WHERE id = %s", (category_id,))
        await conn.commit()
    conn.close()
    return {"message": f"Category {category_id} soft-deleted (status = 0)"}


# ✅ Get all categories (public)
async def get_all_categories_public():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("SELECT * FROM category WHERE status = 1")
        categories = await cursor.fetchall()

        # Fetch related images
        for category in categories:
            await cursor.execute(
                "SELECT id, image_id, path FROM category_images WHERE category_id = %s",
                (category["id"],)
            )
            category["images"] = await cursor.fetchall()

    conn.close()
    return categories
