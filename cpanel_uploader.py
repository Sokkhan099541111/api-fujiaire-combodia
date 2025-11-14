import os
import paramiko
import posixpath
from dotenv import load_dotenv

load_dotenv()

CPANEL_HOST = os.getenv("CPANEL_HOST")
CPANEL_PORT = int(os.getenv("CPANEL_PORT", 22))
CPANEL_USERNAME = os.getenv("CPANEL_USERNAME")
CPANEL_PASSWORD = os.getenv("CPANEL_PASSWORD")
CPANEL_UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/public_html/uploads").rstrip("/")


def upload_to_cpanel(file_bytes: bytes, filename: str) -> bool:
    try:
        print(f"Connecting to {CPANEL_HOST}:{CPANEL_PORT} as {CPANEL_USERNAME}...")

        transport = paramiko.Transport((CPANEL_HOST, CPANEL_PORT))

        transport.get_security_options().ciphers = [
            'aes128-ctr', 'aes192-ctr', 'aes256-ctr',
            'aes128-cbc', 'aes192-cbc', 'aes256-cbc'
        ]

        transport.connect(username=CPANEL_USERNAME, password=CPANEL_PASSWORD)

        sftp = paramiko.SFTPClient.from_transport(transport)

        remote_path = posixpath.join(CPANEL_UPLOAD_PATH, filename)

        print(f"Uploading to remote path: {remote_path}...")

        with sftp.open(remote_path, "wb") as f:
            f.write(file_bytes)

        print("Upload successful!")

        sftp.close()
        transport.close()

        return True

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return False
