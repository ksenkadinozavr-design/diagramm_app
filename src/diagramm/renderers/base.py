from __future__ import annotations

import shutil
import subprocess
from pathlib import Path


class RenderError(RuntimeError):
    """Raised when external renderers are unavailable or fail."""


def require_command(command: str, install_hint: str) -> str:
    path = shutil.which(command)
    if not path:
        raise RenderError(f"Missing '{command}'. {install_hint}")
    return path


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def run_command(command: list[str], error_message: str) -> None:
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        stderr = exc.stderr.strip() if exc.stderr else ""
        suffix = f" Details: {stderr}" if stderr else ""
        raise RenderError(f"{error_message}.{suffix}") from exc
