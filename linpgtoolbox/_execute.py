import subprocess
import sys

# the version that currently selected for commands
_PYTHON_VERSION: str = f"{sys.version_info.major}.{sys.version_info.minor}"


# if the current platform is windows
def is_using_windows() -> bool:
    return sys.platform.startswith("win")


# check if docker has been enabled
def is_docker_disable() -> bool:
    try:
        # Run the `docker --version` command
        return (
            subprocess.run(
                ["docker", "--version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            ).returncode
            != 0
        )
    except FileNotFoundError:
        return True


# execute a python commend
def execute_python(*cmd: str, cwd: str | None = None) -> None:
    subprocess.check_call(
        (
            ["py", f"-{_PYTHON_VERSION}", *cmd]
            if is_using_windows()
            else [f"python{_PYTHON_VERSION}", *cmd]
        ),
        cwd=cwd,
    )


# set the python version used for commands
def set_python_version(v: str) -> None:
    global _PYTHON_VERSION
    _PYTHON_VERSION = v


# get the version of current python selected
def get_current_python_version() -> list[str]:
    return _PYTHON_VERSION.split(".")
