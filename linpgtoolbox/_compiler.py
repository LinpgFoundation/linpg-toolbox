import os
import sys
from typing import IO, TYPE_CHECKING

if TYPE_CHECKING:
    from multiprocessing.sharedctypes import Synchronized

import mypy.stubgen
from Cython.Build import cythonize  # type: ignore

# setuptools.setup import cannot be after Cython.Build
from setuptools import setup


# Compile method
def _compile_file(
    _source_folder: str,
    _path: str,
    _keep_c: bool,
    _debug_mode: bool,
    _silent: bool = False,
    _progress_counter: "Synchronized[int] | None" = None,
) -> None:
    # If silent mode, redirect stdout and stderr to devnull
    _original_stdout = sys.stdout
    _original_stderr = sys.stderr
    _devnull_out: IO[str] | None = None
    _devnull_err: IO[str] | None = None
    if _silent:
        _devnull_out = open(os.devnull, "w")
        _devnull_err = open(os.devnull, "w")
        sys.stdout = _devnull_out
        sys.stderr = _devnull_err
    try:
        setup(
            ext_modules=cythonize(  # type: ignore
                _path, show_all_warnings=_debug_mode, annotate=_debug_mode
            )
        )
        # Delete c/cpp files
        if not _keep_c:
            file_path_without_ext: str = _path[: _path.rfind(".")]
            _c_file: str = file_path_without_ext + ".c"
            _cpp_file: str = file_path_without_ext + ".cpp"
            if os.path.exists(_c_file):
                os.remove(_c_file)
            elif os.path.exists(_cpp_file):
                os.remove(_cpp_file)
        # Generate .pyi typing hint files
        if _path.endswith(".py"):
            mypy.stubgen.main(
                [
                    _path,
                    "-o",
                    os.path.dirname(_source_folder),
                    "--include-docstrings",
                    "--include-private",
                ]
            )
        # Delete original py file (only executed after all above steps succeed)
        os.remove(_path)
    finally:
        # Update progress counter
        if _progress_counter is not None:
            with _progress_counter.get_lock():
                _progress_counter.value += 1
        # Restore stdout and stderr
        if _silent:
            sys.stdout = _original_stdout
            sys.stderr = _original_stderr
            if _devnull_out is not None:
                _devnull_out.close()
            if _devnull_err is not None:
                _devnull_err.close()


if __name__ == "__main__":
    import json
    import re
    import time
    from glob import glob
    from multiprocessing import Process, Value
    from tempfile import gettempdir
    from typing import Any

    # Load global parameters
    _data_path: str = os.path.join(gettempdir(), "linpgtoolbox_builder_cache.json")
    with open(_data_path, "r", encoding="utf-8") as f:
        _data: dict[str, Any] = json.load(f)
        # Whether to enable debug mode
        _debug_mode: bool = bool(_data["debug_mode"])
        # Whether to keep c files
        _keep_c: bool = bool(_data["keep_c"])
        # Whether to enable multiprocessing
        _enable_multiprocessing: bool = bool(_data["enable_multiprocessing"])
        # Path to store source code files
        _source_folder: str = str(_data["source_folder"])
        # Keywords of files to ignore
        _ignores: tuple[str, ...] = tuple(_data["ignores"])

    # Whether to show compile messages (enabled via command line argument, default off for multiprocessing, shows progress bar)
    _show_compile_messages: bool = "--show-compile-messages" in sys.argv

    # Remove parameter file
    os.remove(_data_path)

    # Whether silent mode (enabled when multiprocessing and compile messages are not requested)
    _silent: bool = _enable_multiprocessing and not _show_compile_messages

    # Shared progress counter
    _progress_counter = Value("i", 0)

    # Show progress bar
    def _print_progress_bar(completed: int, total: int) -> None:
        if total == 0:
            return
        bar_length: int = 40
        filled: int = int(bar_length * completed / total)
        bar: str = "#" * filled + "-" * (bar_length - filled)
        percent: float = 100.0 * completed / total
        sys.stdout.write(f"\rCompiling: [{bar}] {percent:5.1f}% ({completed}/{total})")
        sys.stdout.flush()
        if completed >= total:
            sys.stdout.write("\n")

    # Compile process management module
    class _CompileProcessManager:
        # List to store processes
        __processes: list[Process] = []

        # Whether to ignore file
        @classmethod
        def __if_ignore(cls, _path: str) -> bool:
            return any(re.match(pattern, _path) for pattern in _ignores)

        # Create compile process
        @classmethod
        def __generate_process(cls, _path: str) -> None:
            if not os.path.isdir(_path):
                if (
                    _path.endswith(".py") or _path.endswith(".pyx")
                ) and not cls.__if_ignore(_path):
                    # If using multiprocessing
                    if _enable_multiprocessing is True:
                        cls.__processes.append(
                            Process(
                                target=_compile_file,
                                args=(
                                    _source_folder,
                                    _path,
                                    _keep_c,
                                    _debug_mode,
                                    _silent,
                                    _progress_counter,
                                ),
                            )
                        )
                    # If not using multiprocessing
                    else:
                        _compile_file(_source_folder, _path, _keep_c, _debug_mode)
            elif "pyinstaller" not in _path and "pycache" not in _path:
                if not cls.__if_ignore(_path):
                    for file_in_dir in glob(os.path.join(_path, "*")):
                        cls.__generate_process(file_in_dir)

        # Get total number of processes
        @classmethod
        def total(cls) -> int:
            return len(cls.__processes)

        # Initialize compile processes
        @classmethod
        def init(cls) -> None:
            if os.path.exists(_source_folder):
                cls.__generate_process(_source_folder)
            else:
                _source_file: str = _source_folder + ".py"
                if os.path.exists(_source_file):
                    cls.__generate_process(_source_file)

        # Start all processes
        @classmethod
        def start(cls) -> None:
            for _process in cls.__processes:
                _process.start()

        # Ensure all processes finish before exiting
        @classmethod
        def join(cls) -> None:
            for _process in cls.__processes:
                _process.join()

    # Initialize, create processes
    _CompileProcessManager.init()
    # Start all processes
    _CompileProcessManager.start()

    # If silent mode, show progress bar
    if _silent and _CompileProcessManager.total() > 0:
        _total: int = _CompileProcessManager.total()
        _print_progress_bar(0, _total)
        while _progress_counter.value < _total:
            _print_progress_bar(_progress_counter.value, _total)
            time.sleep(0.2)
        _print_progress_bar(_total, _total)
    # Do not exit before processes finish
    _CompileProcessManager.join()
