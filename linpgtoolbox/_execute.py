import sys
from subprocess import check_call


def execute_python(*cmd: str, cwd: str | None = None) -> None:
    if sys.platform.startswith("win"):
        check_call(["py", f"-3.{sys.version_info.minor}", *cmd], cwd=cwd)
    else:
        check_call([f"python3.{sys.version_info.minor}", *cmd], cwd=cwd)
