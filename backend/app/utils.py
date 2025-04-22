import os
import shutil
from fastapi import UploadFile
from .config import settings
import logging

logger = logging.getLogger(__name__)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Saves an uploaded file temporarily and returns its path."""
    filename = os.path.basename(upload_file.filename) # Basic sanitization
    temp_file_path = os.path.join(settings.upload_dir, filename)
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(upload_file.file, buffer)
    except Exception as e:
        logger.error(f"Error saving file {filename}: {e}")
        raise
    finally:
        await upload_file.close()
    logger.info(f"File '{filename}' saved to '{temp_file_path}'")
    return temp_file_path

def cleanup_file(file_path: str):
    """Removes a file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"Cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.error(f"Error cleaning up file {file_path}: {e}")