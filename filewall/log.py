"""logging service for filewall with console and rotating file output"""

import logging
import logging.handlers
import os
import re
from collections import deque

from filewall.env import env

# matches a formatted line: "[2026-07-08 21:04:15] INFO in module.func: message"
_LINE_RE = re.compile(r"^\[(?P<time>[\d\-: ]+)\] (?P<level>\w+) in (?P<source>[\w.<>]+): (?P<message>.*)$")


class Log:
    """application logger with console and rotating file output"""

    def __init__(self):
        self.log = logging.getLogger("filewall_log")
        self.logfile: str | None = None

        level = getattr(logging, env.log_level, logging.INFO)
        self.log.setLevel(level)

    def init_filewall(self, instance_path: str):
        """attach console and rotating file handlers writing to the instance dir"""
        logfile = os.path.join(instance_path, "filewall.log")
        self.logfile = logfile

        if not self.log.hasHandlers():
            formatter = logging.Formatter(
                "[%(asctime)s] %(levelname)s in %(module)s.%(funcName)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
            )

            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)

            rotation_handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=5 * 1024 * 1024, backupCount=2)
            rotation_handler.setFormatter(formatter)

            self.log.addHandler(console_handler)
            self.log.addHandler(rotation_handler)

        return self.log

    def info(self, message):
        self.log.info(message, stacklevel=2)

    def debug(self, message):
        self.log.debug(message, stacklevel=2)

    def error(self, message):
        self.log.error(message, stacklevel=2)

    def warning(self, message):
        self.log.warning(message, stacklevel=2)

    def read_entries(self, limit: int = 500) -> list[dict]:
        """most recent parsed log entries, oldest first

        continuation lines (tracebacks) get appended to the previous entry,
        lines without the standard format are kept as raw message entries
        """
        if not self.logfile or not os.path.isfile(self.logfile):
            return []

        # only keep the tail in memory, the file rotates at a few mb
        with open(self.logfile, encoding="utf-8", errors="replace") as handle:
            lines = deque(handle, maxlen=limit)

        entries: list[dict] = []
        for line in lines:
            line = line.rstrip("\n")
            match = _LINE_RE.match(line)
            if match:
                entries.append(
                    {
                        "time": match["time"],
                        "level": match["level"].upper(),
                        "source": match["source"],
                        "message": match["message"],
                    }
                )
            elif entries:
                entries[-1]["message"] += "\n" + line
            elif line:
                entries.append({"time": "", "level": "", "source": "", "message": line})

        return entries


logger = Log()
