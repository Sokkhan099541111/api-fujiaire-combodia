# utils/ftp_uploader.py
from ftplib import FTP
import os
from datetime import datetime

def upload_to_cpanel_ftp(ftp_host, ftp_user, ftp_pass, file, upload_path="/public_html/uploads"):
    try:
        ftp = FTP(ftp_host, timeout=30)
        ftp.login(ftp_user, ftp_pass)

        # Create folder if not exists
        try:
            ftp.cwd(upload_path)
        except:
            parts = upload_path.split("/")
            path = ""
            for p in parts:
                if p == "":
                    continue
                path += f"/{p}"
                try:
                    ftp.mkd(path)
                except:
                    pass

        ftp.cwd(upload_path)

        # Generate file name
        ext = os.path.splitext(file.filename)[1]
        file_name = datetime.now().strftime("%Y%m%d%H%M%S") + ext

        # Upload
        ftp.storbinary(f"STOR {file_name}", file.file)

        ftp.quit()

        return {
            "status": "success",
            "file_url": f"https://{ftp_host.replace('ftp.', '')}/uploads/{file_name}",
            "file_name": file_name
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}
