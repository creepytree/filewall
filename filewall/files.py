"""filesystem service for the mounted data dir

lists all files below the data dir (recursive) with bare stat infos and
handles safe path resolution so nothing outside the mount is reachable,
generates cached webp thumbnails so the gallery never ships full images
"""

from __future__ import annotations

import glob
import hashlib
import os
from datetime import datetime

from PIL import Image

from filewall.log import logger

# extensions the ui offers a large view for
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".bmp", ".ico", ".avif"}

# bounding box for gallery thumbnails (2x the card size for retina)
THUMB_SIZE = 480


class FileStore:
    def __init__(self):
        self._root: str | None = None
        self._thumb_dir: str | None = None

    def init_filewall(self, data_path: str, instance_path: str) -> None:
        self._root = os.path.realpath(data_path)
        self._thumb_dir = os.path.join(instance_path, "thumbs")
        os.makedirs(self._thumb_dir, exist_ok=True)

    @property
    def root(self) -> str:
        assert self._root is not None, "FileStore not initialized"
        return self._root

    def resolve(self, rel_path: str) -> str | None:
        """absolute path for a relative one, none if it escapes the data dir"""
        if not rel_path or rel_path.startswith(("/", "\\")):
            return None
        full_path = os.path.realpath(os.path.join(self.root, rel_path))
        if full_path == self.root or not full_path.startswith(self.root + os.sep):
            return None
        return full_path

    def list_files(self) -> list[dict]:
        """all files below the data dir with bare infos, newest first"""
        results: list[dict] = []
        digests: set[str] = set()
        for dirpath, dirnames, filenames in os.walk(self.root):
            # skip hidden dirs like .git
            dirnames[:] = [name for name in dirnames if not name.startswith(".")]
            for filename in filenames:
                if filename.startswith("."):
                    continue
                full_path = os.path.join(dirpath, filename)
                try:
                    stat = os.stat(full_path)
                except OSError:
                    continue
                rel_path = os.path.relpath(full_path, self.root).replace(os.sep, "/")
                digests.add(hashlib.sha1(rel_path.encode()).hexdigest())
                results.append(
                    {
                        "path": rel_path,
                        "name": filename,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M"),
                        "created": datetime.fromtimestamp(stat.st_ctime).strftime("%Y-%m-%d %H:%M"),
                        "is_image": os.path.splitext(filename)[1].lower() in IMAGE_EXTENSIONS,
                    }
                )
        self._prune_orphan_thumbs(digests)
        results.sort(key=lambda entry: entry["modified"], reverse=True)
        return results

    def _prune_orphan_thumbs(self, digests: set[str]) -> None:
        """drop cached thumbs of files that no longer exist (removed outside the ui)"""
        assert self._thumb_dir is not None
        for thumb in os.listdir(self._thumb_dir):
            if thumb.split("-", 1)[0] not in digests:
                try:
                    os.remove(os.path.join(self._thumb_dir, thumb))
                except OSError:
                    pass

    def thumbnail(self, rel_path: str, full_path: str) -> str | None:
        """cached thumbnail for the file, none if it cannot be generated"""
        assert self._thumb_dir is not None, "FileStore not initialized"
        # browsers render svg small on their own, pillow cannot
        if os.path.splitext(full_path)[1].lower() == ".svg":
            return None

        stat = os.stat(full_path)
        digest = hashlib.sha1(rel_path.encode()).hexdigest()
        cached = os.path.join(self._thumb_dir, f"{digest}-{int(stat.st_mtime)}-{stat.st_size}.webp")
        if os.path.isfile(cached):
            return cached

        try:
            with Image.open(full_path) as image:
                image.thumbnail((THUMB_SIZE, THUMB_SIZE))
                if image.mode not in ("RGB", "RGBA"):
                    image = image.convert("RGBA")
                self._purge_thumbs(digest)
                image.save(cached, "WEBP", quality=80)
        except Exception as error:
            logger.debug(f"No thumbnail for '{rel_path}': {error}")
            return None
        logger.debug(f"Generated thumbnail for '{rel_path}'")
        return cached

    def _purge_thumbs(self, digest: str) -> None:
        """drop stale thumbnail versions of a file"""
        assert self._thumb_dir is not None
        for old in glob.glob(os.path.join(self._thumb_dir, f"{digest}-*")):
            try:
                os.remove(old)
            except OSError:
                pass

    def delete(self, rel_paths: list[str]) -> tuple[list[str], list[str]]:
        """delete the given files, returns (deleted, failed)"""
        deleted: list[str] = []
        failed: list[str] = []
        for rel_path in rel_paths:
            full_path = self.resolve(rel_path)
            if not full_path or not os.path.isfile(full_path):
                failed.append(rel_path)
                continue
            try:
                os.remove(full_path)
                self._purge_thumbs(hashlib.sha1(rel_path.encode()).hexdigest())
                deleted.append(rel_path)
            except OSError:
                failed.append(rel_path)
        return deleted, failed


files = FileStore()
