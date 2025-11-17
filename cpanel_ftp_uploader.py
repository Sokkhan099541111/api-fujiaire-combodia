import aioftp
import ssl
import os


FTP_HOST = os.getenv("CPANEL_FTP_HOST")
FTP_USER = os.getenv("CPANEL_FTP_USER")
FTP_PASS = os.getenv("CPANEL_FTP_PASSWORD")
FTP_UPLOAD_DIR = os.getenv("CPANEL_FTP_UPLOAD_DIR", "/public_html/uploads").rstrip("/")


if not all([FTP_HOST, FTP_USER, FTP_PASS]):
    raise EnvironmentError("Missing one or more required FTP environment variables: "
                           "CPANEL_FTP_HOST, CPANEL_FTP_USER, CPANEL_FTP_PASSWORD")


async def upload_to_ftp(file_bytes: bytes, filename: str) -> bool:
    try:
        # For plain FTP (no SSL)
        async with aioftp.Client.context(
            host=FTP_HOST,
            user=FTP_USER,
            password=FTP_PASS,
            ssl=None,  # disable SSL/TLS
            socket_timeout=30
        ) as client:

            try:
                await client.make_directory(FTP_UPLOAD_DIR)
            except aioftp.StatusCodeError as e:
                if not e.received_codes or "550" not in e.received_codes:
                    raise

            remote_path = f"{FTP_UPLOAD_DIR}/{filename}"
            async with client.upload_stream(remote_path) as stream:
                await stream.write(file_bytes)

        return True

    except Exception as e:
        print(f"FTP Upload Error: {e}")
        return False

