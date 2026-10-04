"""environment parsing and application configuration"""

from __future__ import annotations

import os
from dataclasses import dataclass


def _get_str(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _get_bool(name: str, default: bool = False) -> bool:
    raw_value = _get_str(name).lower()
    if not raw_value:
        return default

    return raw_value in {"1", "true", "yes", "on"}


def _get_int(name: str, default: int) -> int:
    raw_value = _get_str(name)
    if not raw_value:
        return default

    try:
        return int(raw_value)
    except ValueError:
        return default


def _get_base_path() -> str:
    base_path = _get_str("BASE_PATH")

    if base_path:
        if not base_path.startswith("/"):
            base_path = "/" + base_path
        base_path = base_path.rstrip("/")

    return base_path


@dataclass(frozen=True)
class EnvConfig:
    base_path: str
    data_dir: str
    instance_dir: str
    log_level: str
    login_enabled: bool
    login_user: str
    login_password: str
    login_timeout: int  # session lifetime in minutes


def load_env() -> EnvConfig:
    return EnvConfig(
        base_path=_get_base_path(),
        data_dir=_get_str("DATA_DIR"),
        instance_dir=_get_str("INSTANCE_DIR"),
        log_level=_get_str("LOG_LEVEL", "DEBUG").upper(),
        login_enabled=_get_bool("LOGIN"),
        login_user=_get_str("LOGIN_USER"),
        login_password=_get_str("LOGIN_PW"),
        login_timeout=_get_int("LOGIN_TIMEOUT", 60),
    )


env = load_env()
