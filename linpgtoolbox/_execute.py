import sys
from subprocess import check_call

# the python version of current environment
_DEFAULT_PYTHON_VERSION: str = f"{sys.version_info.major}.{sys.version_info.minor}"

# the version that currently selected for commands
_SELECTED_PYTHON_VERSION: str = _DEFAULT_PYTHON_VERSION


# if the current platform is windows
def is_using_windows() -> bool:
    return sys.platform.startswith("win")


# execute a python commend
def execute_python(*cmd: str, cwd: str | None = None) -> None:
    check_call(
        (
            ["py", f"-{_SELECTED_PYTHON_VERSION}", *cmd]
            if is_using_windows()
            else [f"python{_SELECTED_PYTHON_VERSION}", *cmd]
        ),
        cwd=cwd,
    )


# set the python version used for commands
def set_python_version(v: str = _DEFAULT_PYTHON_VERSION) -> None:
    global _SELECTED_PYTHON_VERSION
    _SELECTED_PYTHON_VERSION = v


# get the version of current python selected
def get_current_python_version() -> list[str]:
    return _SELECTED_PYTHON_VERSION.split(".")
