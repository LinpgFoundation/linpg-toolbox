import sys
from subprocess import check_call

# the version that currently selected for commands
_PYTHON_VERSION: str = f"3.{sys.version_info.minor}"


# execute a python commend
def execute_python(*cmd: str, cwd: str | None = None) -> None:
    if sys.platform.startswith("win"):
        check_call(["py", f"-{_PYTHON_VERSION}", *cmd], cwd=cwd)
    else:
        check_call([f"python{_PYTHON_VERSION}", *cmd], cwd=cwd)


# set the python version used for commands
def set_python_version(v: str) -> None:
    global _PYTHON_VERSION
    _PYTHON_VERSION = v
