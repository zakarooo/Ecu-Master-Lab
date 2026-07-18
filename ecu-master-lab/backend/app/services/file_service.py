import hashlib
import os
import re
import shutil
from pathlib import Path
from app.core.config import settings


def save_uploaded_file(file_content: bytes, filename: str, project_id: int) -> dict:
    project_dir = settings.UPLOAD_DIR / str(project_id)
    project_dir.mkdir(parents=True, exist_ok=True)

    original_dir = project_dir / "original"
    original_dir.mkdir(exist_ok=True)

    safe_name = re.sub(r'[^\w\-.]', '_', filename)
    file_path = original_dir / safe_name
    with open(file_path, "wb") as f:
        f.write(file_content)

    file_hash = hashlib.sha256(file_content).hexdigest()
    backup_path = project_dir / f"original_backup_{file_hash[:8]}.bin"
    shutil.copy2(file_path, backup_path)

    return {
        "file_path": str(file_path),
        "file_size": len(file_content),
        "file_hash": file_hash,
        "backup_path": str(backup_path),
    }


def save_version(file_path: str, project_id: int, version_number: int, label: str = None) -> dict:
    project_dir = settings.UPLOAD_DIR / str(project_id)
    versions_dir = project_dir / "versions"
    versions_dir.mkdir(exist_ok=True)

    ext = Path(file_path).suffix
    version_filename = f"version_{version_number}{ext}"
    version_path = versions_dir / version_filename

    shutil.copy2(file_path, version_path)

    with open(version_path, "rb") as f:
        content = f.read()
        file_hash = hashlib.sha256(content).hexdigest()

    return {
        "file_path": str(version_path),
        "file_hash": file_hash,
        "version_number": version_number,
        "label": label or f"Version {version_number}",
    }


def get_file_info(file_path: str) -> dict:
    if not os.path.exists(file_path):
        return None
    stat = os.stat(file_path)
    with open(file_path, "rb") as f:
        content = f.read()
        file_hash = hashlib.sha256(content).hexdigest()
    return {
        "file_path": file_path,
        "file_size": stat.st_size,
        "file_hash": file_hash,
        "filename": os.path.basename(file_path),
    }
