import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

CPANEL_HOST = os.getenv("CPANEL_HOST")
CPANEL_PORT = int(os.getenv("CPANEL_PORT", 22))
CPANEL_USERNAME = os.getenv("CPANEL_USERNAME")
CPANEL_PASSWORD = os.getenv("CPANEL_PASSWORD")
CPANEL_UPLOAD_PATH = os.getenv("UPLOAD_PATH")

def upload_to_cpanel(file_bytes: bytes, filename: str) -> bool:
    try:
        transport = paramiko.Transport((CPANEL_HOST, CPANEL_PORT))
        transport.connect(username=CPANEL_USERNAME, password=CPANEL_PASSWORD)

        sftp = paramiko.SFTPClient.from_transport(transport)
        remote_path = os.path.join(CPANEL_UPLOAD_PATH, filename)

        with sftp.open(remote_path, "wb") as f:
            f.write(file_bytes)

        sftp.close()
        transport.close()

        return True

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return False
