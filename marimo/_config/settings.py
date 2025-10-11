# Copyright 2024 Marimo. All rights reserved.
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field


@dataclass
class GlobalSettings:
    DEVELOPMENT_MODE: bool = False
    QUIET: bool = False
    YES: bool = False
    CHECK_STATUS_UPDATE: bool = False
    TRACING: bool = os.getenv("MARIMO_TRACING", "false") in ("true", "1")
    PROFILE_DIR: str | None = None
    LOG_LEVEL: int = logging.WARNING
    MANAGE_SCRIPT_METADATA: bool = os.getenv(
        "MARIMO_MANAGE_SCRIPT_METADATA", "false"
    ) in ("true", "1")
    IN_SECURE_ENVIRONMENT: bool = os.getenv(
        "MARIMO_IN_SECURE_ENVIRONMENT", "false"
    ) in ("true", "1")
    DISABLE_HOME_PAGE: bool = False
    DISABLE_TERMINAL: bool = False
    DISABLE_PACKAGE_INSTALLATION: bool = False
    DISABLED_PANELS: list[str] = field(default_factory=list)


GLOBAL_SETTINGS = GlobalSettings()
