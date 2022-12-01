from os import path as OS_PATH
from os import remove as OS_REMOVE
from subprocess import check_call

from setuptools import setup  # setuptools.setup import不可以在Cython.Build之后
from Cython.Build import cythonize  # type: ignore


# 编译方法
def _compile_file(
    _source_folder: str,
    _path: str,
    _keep_c: bool,
    _debug_mode: bool,
    _compiler_directives: dict,
) -> None:
    setup(
        ext_modules=cythonize(
            _path,
            show_all_warnings=_debug_mode,
            annotate=_debug_mode,
            language_level="3",
            compiler_directives=_compiler_directives,
        )
    )
    # 删除c文件
    if not _keep_c:
        OS_REMOVE(_path.replace(".py", ".c"))
    # 生成pyi后缀的typing提示文件
    check_call(["stubgen", _path, "-o", OS_PATH.dirname(_source_folder)])
    # 删除原始py文件
    OS_REMOVE(_path)


if __name__ == "__main__":

    import json
    from glob import glob
    from multiprocessing import Process

    # 加载全局参数
    with open("builder_data_cache.json", "r", encoding="utf-8") as f:
        Data: dict = json.load(f)
        # 是否启用debug模式
        _debug_mode: bool = bool(Data["debug_mode"])
        # 是否保存c文件
        _keep_c: bool = bool(Data["keep_c"])
        # 其他次要参数
        _compiler_directives: dict = dict(Data["compiler_directives"])
        # 是否启用多线程
        _enable_multiprocessing: bool = bool(Data["enable_multiprocessing"])
        # 储存源代码的文件的路径
        _source_folder: str = str(Data["source_folder"])
        # 需要忽略的文件的关键词
        _ignore_key_words: tuple = tuple(Data["ignore_key_words"])

    # 移除参数文件
    OS_REMOVE("builder_data_cache.json")

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
            if not OS_PATH.isdir(_path):
                if _path.endswith(".py") and not cls.__if_ignore(_path):
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
                        )
            elif "pyinstaller" not in _path and "pycache" not in _path:
                if not cls.__if_ignore(_path):
                    for file_in_dir in glob(OS_PATH.join(_path, "*")):
                        cls.__generate_process(file_in_dir)

        # 初始化编译进程
        @classmethod
        def init(cls) -> None:
            if OS_PATH.exists(_source_folder):
                cls.__generate_process(_source_folder)
            else:
                _source_file: str = _source_folder + ".py"
                if OS_PATH.exists(_source_file):
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
