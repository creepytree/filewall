"""json api for the file gallery and the log view"""

from __future__ import annotations

import os
import tempfile
import zipfile

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from starlette.background import BackgroundTask

from filewall.files import files
from filewall.log import logger

api = APIRouter(prefix="/api")


class PathsPayload(BaseModel):
    paths: list[str] = Field(min_length=1, max_length=10000)


@api.get("/files")
def list_files():
    listing = files.list_files()
    logger.debug(f"Listed {len(listing)} files")
    return listing


@api.get("/files/raw")
def raw_file(path: str, download: bool = False):
    """serve a file from the data dir (image view / thumbnails / single download)"""
    full_path = files.resolve(path)
    if not full_path or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    if download:
        logger.info(f"Downloaded file '{path}'")
        return FileResponse(full_path, filename=os.path.basename(full_path))
    return FileResponse(full_path)


@api.get("/files/thumb")
def thumb_file(path: str):
    """small cached thumbnail for the gallery, falls back to the raw file"""
    full_path = files.resolve(path)
    if not full_path or not os.path.isfile(full_path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(files.thumbnail(path, full_path) or full_path)


@api.post("/files/download")
def download_files(payload: PathsPayload):
    """bundle the given files into a zip download"""
    resolved = [(path, files.resolve(path)) for path in payload.paths]
    resolved = [(path, full) for path, full in resolved if full and os.path.isfile(full)]
    if not resolved:
        raise HTTPException(status_code=404, detail="No file found")

    # temp zip on disk, removed after the response is sent
    handle = tempfile.NamedTemporaryFile(delete=False, suffix=".zip")
    with zipfile.ZipFile(handle, "w", zipfile.ZIP_DEFLATED) as archive:
        for path, full_path in resolved:
            archive.write(full_path, arcname=path)
    handle.close()

    logger.info(f"Downloaded {len(resolved)} files as zip")
    return FileResponse(
        handle.name,
        filename="filewall.zip",
        media_type="application/zip",
        background=BackgroundTask(os.remove, handle.name),
    )


@api.post("/files/delete")
def delete_files(payload: PathsPayload):
    deleted, failed = files.delete(payload.paths)
    for path in deleted:
        logger.info(f"Deleted file '{path}'")
    for path in failed:
        logger.warning(f"Could not delete '{path}'")
    if not deleted and failed:
        raise HTTPException(status_code=404, detail="No file could be deleted")
    return {"deleted": deleted, "failed": failed}


# -- log -------------------------------------------------------------------


@api.get("/log")
def read_log(limit: int = 500):
    return logger.read_entries(limit=min(max(limit, 1), 2000))
