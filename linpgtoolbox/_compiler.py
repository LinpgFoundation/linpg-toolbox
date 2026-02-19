import os
import sys
from typing import IO, TYPE_CHECKING

if TYPE_CHECKING:
    from multiprocessing.sharedctypes import Synchronized

import mypy.stubgen
from Cython.Build import cythonize  # type: ignore

# setuptools.setup import不可以在Cython.Build之后
from setuptools import setup


# 编译方法
def _compile_file(
    _source_folder: str,
    _path: str,
    _keep_c: bool,
    _debug_mode: bool,
    _silent: bool = False,
    _progress_counter: "Synchronized[int] | None" = None,
) -> None:
    # 如果静默模式，则重定向stdout和stderr到devnull
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
        # 删除c/cpp文件
        if not _keep_c:
            file_path_without_ext: str = _path[: _path.rfind(".")]
            _c_file: str = file_path_without_ext + ".c"
            _cpp_file: str = file_path_without_ext + ".cpp"
            if os.path.exists(_c_file):
                os.remove(_c_file)
            elif os.path.exists(_cpp_file):
                os.remove(_cpp_file)
        # 生成pyi后缀的typing提示文件
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
        # 删除原始py文件（仅在以上步骤全部成功后执行）
        os.remove(_path)
    finally:
        # 更新进度计数器
        if _progress_counter is not None:
            with _progress_counter.get_lock():
                _progress_counter.value += 1
        # 恢复stdout和stderr
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

    # 加载全局参数
    _data_path: str = os.path.join(gettempdir(), "linpgtoolbox_builder_cache.json")
    with open(_data_path, "r", encoding="utf-8") as f:
        _data: dict[str, Any] = json.load(f)
        # 是否启用debug模式
        _debug_mode: bool = bool(_data["debug_mode"])
        # 是否保存c文件
        _keep_c: bool = bool(_data["keep_c"])
        # 是否启用多线程
        _enable_multiprocessing: bool = bool(_data["enable_multiprocessing"])
        # 储存源代码的文件的路径
        _source_folder: str = str(_data["source_folder"])
        # 需要忽略的文件的关键词
        _ignores: tuple[str, ...] = tuple(_data["ignores"])

    # 是否显示编译信息（通过命令行参数开启，多进程时默认关闭，显示进度条）
    _show_compile_messages: bool = "--show-compile-messages" in sys.argv

    # 移除参数文件
    os.remove(_data_path)

    # 是否静默模式（多进程且未要求显示编译信息时启用）
    _silent: bool = _enable_multiprocessing and not _show_compile_messages

    # 共享进度计数器
    _progress_counter = Value("i", 0)

    # 显示进度条
    def _print_progress_bar(completed: int, total: int) -> None:
        if total == 0:
            return
        bar_length: int = 40
        filled: int = int(bar_length * completed / total)
        bar: str = "█" * filled + "░" * (bar_length - filled)
        percent: float = 100.0 * completed / total
        sys.stdout.write(f"\rCompiling: [{bar}] {percent:5.1f}% ({completed}/{total})")
        sys.stdout.flush()
        if completed >= total:
            sys.stdout.write("\n")

    # 编译进程管理模组
    class _CompileProcessManager:
        # 储存进程的列表
        __processes: list[Process] = []

        # 是否忽略文件
        @classmethod
        def __if_ignore(cls, _path: str) -> bool:
            return any(re.match(pattern, _path) for pattern in _ignores)

        # 创建编译进程
        @classmethod
        def __generate_process(cls, _path: str) -> None:
            if not os.path.isdir(_path):
                if (
                    _path.endswith(".py") or _path.endswith(".pyx")
                ) and not cls.__if_ignore(_path):
                    # 如果使用多线程
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
                    # 如果不使用多线程
                    else:
                        _compile_file(_source_folder, _path, _keep_c, _debug_mode)
            elif "pyinstaller" not in _path and "pycache" not in _path:
                if not cls.__if_ignore(_path):
                    for file_in_dir in glob(os.path.join(_path, "*")):
                        cls.__generate_process(file_in_dir)

        # 获取总进程数
        @classmethod
        def total(cls) -> int:
            return len(cls.__processes)

        # 初始化编译进程
        @classmethod
        def init(cls) -> None:
            if os.path.exists(_source_folder):
                cls.__generate_process(_source_folder)
            else:
                _source_file: str = _source_folder + ".py"
                if os.path.exists(_source_file):
                    cls.__generate_process(_source_file)

        # 开始所有的进程
        @classmethod
        def start(cls) -> None:
            for _process in cls.__processes:
                _process.start()

        # 确保所有进程执行完后才退出
        @classmethod
        def join(cls) -> None:
            for _process in cls.__processes:
                _process.join()

    # 初始化，创建进程
    _CompileProcessManager.init()
    # 启动所有进程
    _CompileProcessManager.start()

    # 如果静默模式，则显示进度条
    if _silent and _CompileProcessManager.total() > 0:
        _total: int = _CompileProcessManager.total()
        _print_progress_bar(0, _total)
        while _progress_counter.value < _total:
            _print_progress_bar(_progress_counter.value, _total)
            time.sleep(0.2)
        _print_progress_bar(_total, _total)
    # 在进程结束前不要退出
    _CompileProcessManager.join()
