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
    """
    Uploads a file to the cPanel FTP server using explicit FTPS.

    :param file_bytes: Content of the file as bytes.
    :param filename: Name to save the file as on the FTP server.
    :return: True if upload succeeded, False otherwise.
    """
    try:
        tls_context = ssl.create_default_context()

        # async with aioftp.Client.context(
        #     host=FTP_HOST,
        #     user=FTP_USER,
        #     password=FTP_PASS,
        #     ssl=tls_context,
        #     socket_timeout=30
        # ) as client:

        async with aioftp.Client.context(
            host=FTP_HOST,
            user=FTP_USER,
            password=FTP_PASS,
            ssl=None,  # disable SSL/TLS for plain FTP
            socket_timeout=30,
            port=21  # optional if default
        ) as client:

            # Ensure upload directory exists
            try:
                await client.make_directory(FTP_UPLOAD_DIR)
            except aioftp.StatusCodeError as e:
                # 550 means directory exists or no permission - ignore if exists
                if not e.received_codes or "550" not in e.received_codes:
                    raise

            remote_path = f"{FTP_UPLOAD_DIR}/{filename}"

            async with client.upload_stream(remote_path) as stream:
                await stream.write(file_bytes)

        return True

    except Exception as e:
        print(f"FTP Upload Error: {e}")
        return False
