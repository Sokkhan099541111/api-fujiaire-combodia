import os
import paramiko
from dotenv import load_dotenv

load_dotenv()

CPANEL_HOST = os.getenv("CPANEL_HOST")
CPANEL_PORT = int(os.getenv("CPANEL_PORT", 22))
CPANEL_USERNAME = os.getenv("CPANEL_USERNAME")
CPANEL_PASSWORD = os.getenv("CPANEL_PASSWORD")
CPANEL_UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/public_html/uploads")


def upload_to_cpanel(file_bytes: bytes, filename: str) -> bool:
    try:
        # Create SSH transport
        transport = paramiko.Transport((CPANEL_HOST, CPANEL_PORT))

        # Fix TripleDES Warning – force modern ciphers BEFORE connect()
        transport.get_security_options().ciphers = [
            'aes128-ctr', 'aes192-ctr', 'aes256-ctr',
            'aes128-cbc', 'aes192-cbc', 'aes256-cbc'
        ]

        # Connect
        transport.connect(username=CPANEL_USERNAME, password=CPANEL_PASSWORD)

        # Start SFTP session
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Final upload path
        remote_path = os.path.join(CPANEL_UPLOAD_PATH, filename)

        # Upload file
        with sftp.open(remote_path, "wb") as f:
            f.write(file_bytes)

        # Close
        sftp.close()
        transport.close()

        return True

    except Exception as e:
        print("UPLOAD ERROR:", e)
        return False
