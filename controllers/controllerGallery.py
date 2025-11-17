# controllers/gallery_controller.py

import os
import datetime
import aiomysql
from fastapi.responses import JSONResponse
from db import get_db_connection
from cpanel_ftp_uploader import upload_to_ftp


# ------------------------------------------------------
# CREATE GALLERY ITEM + UPLOAD IMAGE TO CPANEL (FTP)
# ------------------------------------------------------
async def create_gallery(file, user_id: int, image_id: int = None):

    db = await get_db_connection()
    is_pool = hasattr(db, "acquire")
    now = datetime.datetime.utcnow()

    # Generate file name
    filename = f"{now.strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_bytes = await file.read()

    # Upload image to cPanel via FTP
    uploaded = await upload_to_ftp(file_bytes, filename)

    if not uploaded:
        return JSONResponse(status_code=500, content={"error": "FTP upload failed"})

    # Public URL (domain.com/uploads/file.jpg)
    image_url = f"{os.getenv('CPANEL_BASE_URL')}/{filename}"

    # Save to DB
    try:
        query = """
            INSERT INTO gallery (path, image_id, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, 1, %s, %s)
        """

        if is_pool:
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(
                        query, (filename, image_id, user_id, now, now)
                    )
                    await conn.commit()
        else:
            async with db.cursor() as cursor:
                await cursor.execute(
                    query, (filename, image_id, user_id, now, now)
                )
                await db.commit()

        return {"message": "Upload successful", "file": filename, "url": image_url}

    except Exception as e:
        if db:
            await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        if db and not is_pool:
            db.close()


# ------------------------------------------------------
# GET ALL
# ------------------------------------------------------
async def get_all_gallery():
    db = await get_db_connection()
    is_pool = hasattr(db, "acquire")
    rows = []

    try:
        query = "SELECT * FROM gallery WHERE status = 1"

        if is_pool:
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
        else:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                rows = await cursor.fetchall()

        return rows

    finally:
        if db and not is_pool:
            db.close()


# ------------------------------------------------------
# GET BY ID
# ------------------------------------------------------
async def get_gallery_by_id(gallery_id: int):
    db = await get_db_connection()
    is_pool = hasattr(db, "acquire")
    row = None

    try:
        query = "SELECT * FROM gallery WHERE id = %s"

        if is_pool:
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, (gallery_id,))
                    row = await cursor.fetchone()
        else:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (gallery_id,))
                row = await cursor.fetchone()

        return row

    finally:
        if db and not is_pool:
            db.close()


# ------------------------------------------------------
# UPDATE
# ------------------------------------------------------
async def update_gallery(gallery_id: int, image_id: int, user_id: int, status: int):
    db = await get_db_connection()
    is_pool = hasattr(db, "acquire")
    now = datetime.datetime.utcnow()

    try:
        query = """
            UPDATE gallery
            SET image_id=%s, user_id=%s, status=%s, updated_at=%s
            WHERE id=%s
        """

        if is_pool:
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, (image_id, user_id, status, now, gallery_id))
                    await conn.commit()
        else:
            async with db.cursor() as cursor:
                await cursor.execute(query, (image_id, user_id, status, now, gallery_id))
                await db.commit()

        return {"message": "Gallery updated"}

    except Exception as e:
        if db:
            await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        if db and not is_pool:
            db.close()


# ------------------------------------------------------
# SOFT DELETE
# ------------------------------------------------------
async def soft_delete_gallery(gallery_id: int):
    db = await get_db_connection()
    is_pool = hasattr(db, "acquire")

    try:
        query = "UPDATE gallery SET status = 0 WHERE id = %s"

        if is_pool:
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, (gallery_id,))
                    await conn.commit()
        else:
            async with db.cursor() as cursor:
                await cursor.execute(query, (gallery_id,))
                await db.commit()

        return {"message": "Gallery soft-deleted"}

    except Exception as e:
        if db:
            await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        if db and not is_pool:
            db.close()
