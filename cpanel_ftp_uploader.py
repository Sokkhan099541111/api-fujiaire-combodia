# cpanel_ftp_uploader.py

import aioftp
import asyncio
import ssl
import os


# ----------------------------
# ENV CONFIG
# ----------------------------
FTP_HOST = os.getenv("CPANEL_FTP_HOST")            # Example: ftp.example.com
FTP_USER = os.getenv("CPANEL_FTP_USER")            # Full FTP username
FTP_PASS = os.getenv("CPANEL_FTP_PASSWORD")        # FTP password
FTP_UPLOAD_DIR = os.getenv("CPANEL_FTP_UPLOAD_DIR", "/public_html/uploads")


# ----------------------------
# Upload file using FTP (FTPS)
# ----------------------------
async def upload_to_ftp(file_bytes: bytes, filename: str) -> bool:
    try:
        # Enable TLS Explicit FTPS
        tls_context = ssl.create_default_context()

        async with aioftp.Client.context(
            host=FTP_HOST,
            user=FTP_USER,
            password=FTP_PASS,
            ssl=tls_context,           # FTPS (secure)
            socket_timeout=30
        ) as client:

            # Create folder if not exist
            try:
                await client.make_directory(FTP_UPLOAD_DIR)
            except Exception:
                pass  # Directory already exists

            # Path on server
            remote_path = f"{FTP_UPLOAD_DIR}/{filename}"

            # Upload file
            async with client.upload_stream(remote_path) as stream:
                await stream.write(file_bytes)

        return True

    except Exception as e:
        print("FTP Upload Error:", e)
        return False
