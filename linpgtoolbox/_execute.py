import sys
from subprocess import check_call
from typing import Final

_PYTHON_PREFIX: Final[str] = (
    "python" if sys.platform.startswith("win") else f"python3.{sys.version_info[1]}"
)


def execute_python(*cmd: str, cwd: str | None = None) -> None:
    check_call([_PYTHON_PREFIX, *cmd], cwd=cwd)
