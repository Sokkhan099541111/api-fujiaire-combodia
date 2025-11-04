import datetime
import aiomysql
from db import get_db_connection  # should return aiomysql connection


# ===============================
# Get all products (admin)
# ===============================
async def get_all_products():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("""
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                p.detail,
                p.status,
                p.created_at,
                p.updated_at,
                p.category_id,
                p.image_id,
                p.path AS primary_path,
                p.user_id,
                ps.spicification_id,
                pi.id AS product_image_id,
                pi.image_path
            FROM product p
            LEFT JOIN product_spicification ps ON ps.product_id = p.id
            LEFT JOIN product_images pi ON pi.product_id = p.id
            WHERE p.status = 1
            ORDER BY p.id
        """)
        rows = await cursor.fetchall()

    products = {}
    for row in rows:
        pid = row["product_id"]
        if pid not in products:
            products[pid] = {
                "id": pid,
                "name": row["product_name"],
                "detail": row["detail"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "category_id": row["category_id"],
                "image_id": row["image_id"],
                "primary_path": row["primary_path"],
                "user_id": row["user_id"],
                "spicifications": [],
                "images": []
            }
        if row["spicification_id"] and row["spicification_id"] not in products[pid]["spicifications"]:
            products[pid]["spicifications"].append(row["spicification_id"])
        if row["product_image_id"]:
            img_obj = {"id": row["product_image_id"], "path": row["image_path"]}
            if img_obj not in products[pid]["images"]:
                products[pid]["images"].append(img_obj)

    await conn.ensure_closed()
    return list(products.values())


# ===============================
# Get product by ID
# ===============================
async def get_product_by_id(product_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("""
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                p.detail,
                p.status,
                p.created_at,
                p.updated_at,
                p.category_id,
                p.image_id,
                p.path AS primary_path,
                p.user_id,
                ps.spicification_id,
                s.title AS spec_title,
                s.descriptions AS spec_description,
                pi.id AS product_image_id,
                pi.image_path
            FROM product p
            LEFT JOIN product_spicification ps ON ps.product_id = p.id
            LEFT JOIN spicification s ON s.id = ps.spicification_id
            LEFT JOIN product_images pi ON pi.product_id = p.id
            WHERE p.status = 1 AND p.id = %s
        """, (product_id,))
        rows = await cursor.fetchall()

    if not rows:
        await conn.ensure_closed()
        return None

    row = rows[0]
    product = {
        "id": row["product_id"],
        "name": row["product_name"],
        "detail": row["detail"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
        "category_id": row["category_id"],
        "image_id": row["image_id"],
        "primary_path": row["primary_path"],
        "user_id": row["user_id"],
        "spicifications": [],
        "images": []
    }

    for row in rows:
        if row["spicification_id"]:
            spec_obj = {"id": row["spicification_id"], "title": row.get("spec_title"), "description": row.get("spec_description")}
            if spec_obj not in product["spicifications"]:
                product["spicifications"].append(spec_obj)
        if row["product_image_id"]:
            img_obj = {"id": row["product_image_id"], "path": row["image_path"]}
            if img_obj not in product["images"]:
                product["images"].append(img_obj)

    await conn.ensure_closed()
    return product


# ===============================
# Create product
# ===============================
async def create_product(data: dict):
    conn = await get_db_connection()
    now = datetime.datetime.utcnow()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            images = [img for img in data.get("images", []) if img.get("path")]
            first_image = images[0] if images else None

            await cursor.execute("""
                INSERT INTO product 
                (category, category_sub, name, image_id, path, detail, user_id, category_id, status, created_at, updated_at)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """, (
                data.get("category"),
                data.get("category_sub"),
                data.get("name"),
                first_image['id'] if first_image else None,
                first_image['path'] if first_image else None,
                data.get("detail"),
                data.get("user_id"),
                data.get("category_id"),
                data.get("status", 1),
                now,
                now
            ))
            product_id = cursor.lastrowid

            for spic_id in data.get("spicification_id", []):
                await cursor.execute("INSERT INTO product_spicification (product_id, spicification_id) VALUES (%s,%s)", (product_id, spic_id))

            for img in images:
                await cursor.execute("INSERT INTO product_images (product_id, image_path, created_at, updated_at) VALUES (%s,%s,%s,%s)", (product_id, img['path'], now, now))

            await conn.commit()
            return {
                "id": product_id,
                "name": data.get("name"),
                "detail": data.get("detail"),
                "status": data.get("status", 1),
                "created_at": now,
                "updated_at": now,
                "category_id": data.get("category_id"),
                "image_id": first_image['id'] if first_image else None,
                "primary_path": first_image['path'] if first_image else None,
                "user_id": data.get("user_id"),
                "spicifications": data.get("spicification_id", []),
                "images": images
            }

        except Exception as e:
            await conn.rollback()
            return {"error": str(e)}
        finally:
            await conn.ensure_closed()


# ===============================
# Update product
# ===============================
async def update_product(product_id: int, data: dict):
    conn = await get_db_connection()
    updated_at = datetime.datetime.utcnow()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        try:
            await cursor.execute("SELECT created_at FROM product WHERE id=%s", (product_id,))
            row = await cursor.fetchone()
            if not row:
                return {"error": "Product not found"}
            created_at = row["created_at"]

            images = [img for img in data.get("images", []) if img.get("path")]
            first_image = images[0] if images else None

            await cursor.execute("""
                UPDATE product SET
                    category=%s,
                    category_sub=%s,
                    name=%s,
                    image_id=%s,
                    path=%s,
                    detail=%s,
                    user_id=%s,
                    category_id=%s,
                    status=%s,
                    updated_at=%s
                WHERE id=%s
            """, (
                data.get("category"),
                data.get("category_sub"),
                data.get("name"),
                first_image['id'] if first_image else None,
                first_image['path'] if first_image else None,
                data.get("detail"),
                data.get("user_id"),
                data.get("category_id"),
                data.get("status", 1),
                updated_at,
                product_id
            ))

            await cursor.execute("DELETE FROM product_spicification WHERE product_id=%s", (product_id,))
            for spic_id in data.get("spicification_id", []):
                await cursor.execute("INSERT INTO product_spicification (product_id, spicification_id) VALUES (%s,%s)", (product_id, spic_id))

            await cursor.execute("DELETE FROM product_images WHERE product_id=%s", (product_id,))
            for img in images:
                await cursor.execute("INSERT INTO product_images (product_id, image_path, created_at, updated_at) VALUES (%s,%s,%s,%s)", (product_id, img['path'], updated_at, updated_at))

            await conn.commit()
            return {"id": product_id, **data}

        except Exception as e:
            await conn.rollback()
            return {"error": str(e)}
        finally:
            await conn.ensure_closed()


# ===============================
# Soft delete product
# ===============================
async def delete_product(product_id: int):
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("UPDATE product SET status=0, updated_at=%s WHERE id=%s", (datetime.datetime.utcnow(), product_id))
        await conn.commit()
    await conn.ensure_closed()
    return {"message": f"Product {product_id} soft-deleted"}


# ===============================
# Get all products for public (with specs/images)
# ===============================
async def get_all_products_public():
    conn = await get_db_connection()
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute("""
            SELECT 
                p.id AS product_id,
                p.name AS product_name,
                p.detail,
                p.status,
                p.created_at,
                p.updated_at,
                p.category_id,
                p.image_id,
                p.path AS primary_path,
                p.user_id,
                ps.spicification_id,
                s.title AS spec_title,
                s.descriptions AS spec_description,
                pi.id AS product_image_id,
                pi.image_path
            FROM product p
            LEFT JOIN product_spicification ps ON ps.product_id=p.id
            LEFT JOIN spicification s ON s.id=ps.spicification_id
            LEFT JOIN product_images pi ON pi.product_id=p.id
            WHERE p.status=1
            ORDER BY p.id DESC
        """)
        rows = await cursor.fetchall()

    products = {}
    for row in rows:
        pid = row["product_id"]
        if pid not in products:
            products[pid] = {
                "id": pid,
                "name": row["product_name"],
                "detail": row["detail"],
                "status": row["status"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "category_id": row["category_id"],
                "image_id": row["image_id"],
                "primary_path": row["primary_path"],
                "user_id": row["user_id"],
                "spicifications": [],
                "images": []
            }
        if row["spicification_id"]:
            spec_obj = {"id": row["spicification_id"], "title": row["spec_title"], "description": row["spec_description"]}
            if spec_obj not in products[pid]["spicifications"]:
                products[pid]["spicifications"].append(spec_obj)
        if row["product_image_id"]:
            img_obj = {"id": row["product_image_id"], "path": row["image_path"]}
            if img_obj not in products[pid]["images"]:
                products[pid]["images"].append(img_obj)

    await conn.ensure_closed()
    return list(products.values())
