import os
import shutil
import datetime
import aiomysql
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from db import get_db_connection  # async aiomysql pool
from cpanel_ftp_uploader import upload_to_ftp  

router = APIRouter(prefix="/api/gallery", tags=["Gallery"])

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ----------------------------
# CREATE / UPLOAD IMAGE
# ----------------------------
async def create_gallery(file: UploadFile, user_id: int, image_id: Optional[int] = None):
    db = await get_db_connection()
    conn_is_pool = hasattr(db, "acquire")
    now = datetime.datetime.utcnow()

    filename = f"{now.strftime('%Y%m%d%H%M%S')}_{file.filename}"
    file_bytes = await file.read()

    # -----------------------
    # Upload to CPANEL (SFTP)
    # -----------------------
    uploaded = upload_to_ftp(file_bytes, filename)

    if not uploaded:
        return JSONResponse(status_code=500, content={"error": "Failed to upload to cPanel"})

    # Build public image URL
    image_url = f"{os.getenv('CPANEL_BASE_URL')}/{filename}"

    try:
        query = """
            INSERT INTO gallery (path, image_id, user_id, status, created_at, updated_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        if conn_is_pool:
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, (filename, image_id, user_id, 1, now, now))
                    await conn.commit()
        else:
            async with db.cursor() as cursor:
                await cursor.execute(query, (filename, image_id, user_id, 1, now, now))
                await db.commit()

        return {"message": "Upload successful", "file": filename, "url": image_url}

    except Exception as e:
        if db:
            await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        if db and not conn_is_pool:
            db.close()

# ----------------------------
# GET ALL GALLERY
# ----------------------------
@router.get("/")
async def get_all_gallery():
    db = await get_db_connection()
    conn_is_pool = hasattr(db, "acquire")
    rows = []

    try:
        query = "SELECT * FROM gallery WHERE status = 1"
        if conn_is_pool:
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query)
                    rows = await cursor.fetchall()
        else:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query)
                rows = await cursor.fetchall()
    finally:
        if db and not conn_is_pool:
            db.close()

    return {"gallery": rows}


# ----------------------------
# GET BY ID
# ----------------------------
@router.get("/{gallery_id}")
async def get_gallery_by_id(gallery_id: int):
    db = await get_db_connection()
    conn_is_pool = hasattr(db, "acquire")
    row = None
    try:
        query = "SELECT * FROM gallery WHERE id = %s"
        if conn_is_pool:
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, (gallery_id,))
                    row = await cursor.fetchone()
        else:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (gallery_id,))
                row = await cursor.fetchone()
    finally:
        if db and not conn_is_pool:
            db.close()

    if row:
        return {"gallery": row}
    return JSONResponse(status_code=404, content={"error": "Gallery not found"})


# ----------------------------
# UPDATE GALLERY
# ----------------------------
@router.put("/{gallery_id}")
async def update_gallery(
    gallery_id: int,
    image_id: int = Form(None),
    user_id: int = Form(None),
    status: int = Form(1)
):
    db = await get_db_connection()
    conn_is_pool = hasattr(db, "acquire")
    now = datetime.datetime.utcnow()

    try:
        query = """
            UPDATE gallery
            SET image_id = %s, user_id = %s, status = %s, updated_at = %s
            WHERE id = %s
        """
        if conn_is_pool:
            async with db.acquire() as conn:
                async with conn.cursor() as cursor:
                    await cursor.execute(query, (image_id, user_id, status, now, gallery_id))
                    await conn.commit()
        else:
            async with db.cursor() as cursor:
                await cursor.execute(query, (image_id, user_id, status, now, gallery_id))
                await db.commit()

        return {"message": "Gallery updated", "id": gallery_id}

    except Exception as e:
        if db:
            await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        if db and not conn_is_pool:
            db.close()


# ----------------------------
# SOFT DELETE GALLERY
# ----------------------------
@router.delete("/{gallery_id}")
async def delete_gallery(gallery_id: int):
    db = await get_db_connection()
    conn_is_pool = hasattr(db, "acquire")

    try:
        query = "SELECT path FROM gallery WHERE id = %s"
        file_path = None

        if conn_is_pool:
            async with db.acquire() as conn:
                async with conn.cursor(aiomysql.DictCursor) as cursor:
                    await cursor.execute(query, (gallery_id,))
                    row = await cursor.fetchone()
                    if row:
                        file_path = os.path.join(UPLOAD_FOLDER, row["path"])
                        await cursor.execute("UPDATE gallery SET status = 0 WHERE id = %s", (gallery_id,))
                        await conn.commit()
        else:
            async with db.cursor(aiomysql.DictCursor) as cursor:
                await cursor.execute(query, (gallery_id,))
                row = await cursor.fetchone()
                if row:
                    file_path = os.path.join(UPLOAD_FOLDER, row["path"])
                    await cursor.execute("UPDATE gallery SET status = 0 WHERE id = %s", (gallery_id,))
                    await db.commit()

        # Remove file
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        if not file_path:
            return JSONResponse(status_code=404, content={"error": "Gallery not found"})

        return {"message": "Gallery soft-deleted and file removed"}

    except Exception as e:
        if db:
            await db.rollback()
        return JSONResponse(status_code=500, content={"error": str(e)})

    finally:
        if db and not conn_is_pool:
            db.close()
