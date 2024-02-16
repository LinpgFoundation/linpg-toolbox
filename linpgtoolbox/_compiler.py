import os
from subprocess import check_call
from tempfile import gettempdir
from typing import Any

# setuptools.setup import不可以在Cython.Build之后
from setuptools import Extension, setup  # type: ignore
from Cython.Build import cythonize  # type: ignore


# 编译方法
def _compile_file(
    _source_folder: str,
    _path: str,
    _keep_c: bool,
    _debug_mode: bool,
    _compiler_directives: dict[str, Any],
    extra_compile_args: dict[str, list[str]],
) -> None:
    setup(
        ext_modules=cythonize(
            (
                _path
                if _path.endswith(".py")
                else [
                    Extension(
                        os.path.splitext(os.path.basename(_path))[0],
                        [_path],
                        extra_compile_args=extra_compile_args.get(
                            os.path.basename(_path), []
                        ),
                    )
                ]
            ),
            show_all_warnings=_debug_mode,
            annotate=_debug_mode,
            language_level="3",
            compiler_directives=_compiler_directives,
        )
    )
    # 删除c/cpp文件
    if not _keep_c:
        file_path_without_ext: str = _path[: _path.rfind(".")]
        os.remove(
            file_path_without_ext + ".c"
            if os.path.exists(file_path_without_ext + ".c")
            else file_path_without_ext + ".cpp"
        )
    # 生成pyi后缀的typing提示文件
    if _path.endswith(".py"):
        check_call(
            [
                "stubgen",
                _path,
                "-o",
                os.path.dirname(_source_folder),
                "--include-docstrings",
                "--include-private",
            ]
        )
    # 删除原始py文件
    os.remove(_path)


if __name__ == "__main__":
    import json
    from glob import glob
    from multiprocessing import Process

    # 加载全局参数
    _data_path: str = os.path.join(
        gettempdir() if os.name == "nt" else ".", "builder_data_cache.json"
    )
    with open(_data_path, "r", encoding="utf-8") as f:
        _data: dict[str, Any] = json.load(f)
        # 是否启用debug模式
        _debug_mode: bool = bool(_data["debug_mode"])
        # 是否保存c文件
        _keep_c: bool = bool(_data["keep_c"])
        # 其他次要参数
        _compiler_directives: dict[str, Any] = dict(_data["compiler_directives"])
        # 是否启用多线程
        _enable_multiprocessing: bool = bool(_data["enable_multiprocessing"])
        # 储存源代码的文件的路径
        _source_folder: str = str(_data["source_folder"])
        # 需要忽略的文件的关键词
        _ignore_key_words: tuple[str, ...] = tuple(_data["ignore_key_words"])
        # 额外args
        extra_compile_args: dict[str, list[str]] = dict(
            _data.get("extra_compile_args", {})
        )

    # 移除参数文件
    os.remove(_data_path)

    # 编译进程管理模组
    class _CompileProcessManager:
        # 储存进程的列表
        __processes: list[Process] = []

        # 是否忽略文件
        @classmethod
        def __if_ignore(cls, _path: str) -> bool:
            for key_word in _ignore_key_words:
                if key_word in _path:
                    return True
            return False

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
                                    _compiler_directives,
                                    extra_compile_args,
                                ),
                            )
                        )
                    # 如果不使用多线程
                    else:
                        _compile_file(
                            _source_folder,
                            _path,
                            _keep_c,
                            _debug_mode,
                            _compiler_directives,
                            extra_compile_args,
                        )
            elif "pyinstaller" not in _path and "pycache" not in _path:
                if not cls.__if_ignore(_path):
                    for file_in_dir in glob(os.path.join(_path, "*")):
                        cls.__generate_process(file_in_dir)

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
    # 在进程结束前不要退出
    _CompileProcessManager.join()
