import os
import shutil
import sys
import sysconfig
from enum import IntEnum, auto
from glob import glob
from json import dump
from tempfile import gettempdir
from typing import Any, Final

from ._execute import execute_python
from .pkginstaller import PackageInstaller
from .pyinstaller import PyInstaller


# 选择智能合并的模式
class SmartAutoModuleCombineMode(IntEnum):
    DISABLE: Final[int] = auto()
    FOLDER_ONLY: Final[int] = auto()
    ALL_INTO_ONE: Final[int] = auto()


# 搭建和打包文件的系统
class Builder:
    __PATH: Final[str] = os.path.join(os.path.dirname(__file__), "_compiler.py")
    __CACHE_FOLDERS_NEED_REMOVE: Final[tuple[str, ...]] = (
        "dist",
        "Save",
        "build",
        "crash_reports",
        "Cache",
    )
    __DIST_DIR: Final[str] = "dist"

    # 移除指定文件夹中的pycache文件夹
    @classmethod
    def __remove_cache(cls, path: str) -> None:
        for file_path in glob(os.path.join(path, "*")):
            if os.path.isdir(file_path):
                if "pycache" in file_path or "mypy_cache" in file_path:
                    shutil.rmtree(file_path)
                else:
                    cls.__remove_cache(file_path)

    # 如果指定文件夹存在，则移除
    @staticmethod
    def remove(*path: str) -> None:
        for _path in path:
            if os.path.exists(_path):
                shutil.rmtree(_path) if os.path.isdir(_path) else os.remove(_path)

    # 复制文件
    @staticmethod
    def copy(files: tuple[str, ...], target_folder: str) -> None:
        for the_file in files:
            # 如果是文件夹
            if os.path.isdir(the_file):
                shutil.copytree(
                    the_file, os.path.join(target_folder, os.path.basename(the_file))
                )
            else:
                shutil.copy(
                    the_file, os.path.join(target_folder, os.path.basename(the_file))
                )

    # 删除缓存
    @classmethod
    def __clean_up(cls) -> None:
        cls.remove(*cls.__CACHE_FOLDERS_NEED_REMOVE)

    # 合并模块
    @classmethod
    def __combine(cls, _dir_path: str) -> None:
        if os.path.isdir(_dir_path) and os.path.exists(
            init_file_path := os.path.join(_dir_path, "__init__.py")
        ):
            keyWord: Final[str] = "from ."
            keyEndWord: Final[str] = " import *"
            with open(init_file_path, "r", encoding="utf-8") as f:
                _lines: list[str] = f.readlines()
            _index: int = 0
            while _index < len(_lines):
                currentLine: str = _lines[_index].rstrip("\n")
                if (
                    currentLine.startswith(keyWord)
                    and not currentLine.startswith("from ..")
                    and currentLine.endswith(keyEndWord)
                ):
                    pyFilePath: str = os.path.join(
                        _dir_path,
                        currentLine[len(keyWord) : len(currentLine) - len(keyEndWord)]
                        + ".py",
                    )
                    if os.path.exists(pyFilePath):
                        with open(pyFilePath, "r", encoding="utf-8") as f:
                            content: list[str] = f.readlines()
                        cls.remove(pyFilePath)
                        _lines = _lines[:_index] + content + _lines[_index + 1 :]
                    else:
                        _index += 1
                else:
                    _index += 1
            # 如果模块文件夹中只剩__init__.py，则将文件夹转换成一个python文件
            if len(glob(os.path.join(_dir_path, "*"))) <= 1:
                for i in range(len(_lines)):
                    if _lines[i].lstrip().startswith("from .."):
                        _lines[i] = _lines[i].replace("from ..", "from .")
                with open(os.path.join(f"{_dir_path}.py"), "w", encoding="utf-8") as f:
                    f.writelines(_lines)
                shutil.rmtree(_dir_path)
            # 否则则直接将内容写入原__init__.py文件
            else:
                with open(init_file_path, "w", encoding="utf-8") as f:
                    f.writelines(_lines)

    # 编译
    @classmethod
    def compile(
        cls,
        source_folder: str,
        target_folder: str = "src",
        additional_files: tuple[str, ...] = tuple(),
        ignore_key_words: tuple[str, ...] = tuple(),
        smart_auto_module_combine: SmartAutoModuleCombineMode = SmartAutoModuleCombineMode.DISABLE,
        remove_building_cache: bool = True,
        update_the_one_in_sitepackages: bool = False,
        include_pyinstaller_program: bool = False,
        options: dict[str, Any] = {},
    ) -> None:
        # 确保setuptools安装
        PackageInstaller.install("setuptools")
        # 移除cache
        cls.remove(target_folder)
        # 复制文件到新建的src文件夹中，准备开始编译
        os.makedirs(target_folder)
        source_path_in_target_folder: str = os.path.join(target_folder, source_folder)
        shutil.copytree(source_folder, source_path_in_target_folder)
        # 移除不必要的py缓存
        cls.__remove_cache(source_path_in_target_folder)
        # 如果开启了智能模块合并模式
        if smart_auto_module_combine is not SmartAutoModuleCombineMode.DISABLE:
            for _path in glob(os.path.join(source_path_in_target_folder, "*")):
                cls.__combine(_path)
        if smart_auto_module_combine is SmartAutoModuleCombineMode.ALL_INTO_ONE:
            cls.__combine(source_path_in_target_folder)
        # 把数据写入缓存文件以供编译器读取
        builder_options: dict[str, Any] = {
            "source_folder": source_path_in_target_folder,
            "ignore_key_words": ignore_key_words,
            "enable_multiprocessing": True,
            "debug_mode": False,
            "emit_code_comments": False,
            "keep_c": False,
            "compiler_directives": {},
        }
        builder_options.update(options)
        with open(
            os.path.join(
                gettempdir() if os.name == "nt" else ".", "builder_data_cache.json"
            ),
            "w",
            encoding="utf-8",
        ) as f:
            dump(builder_options, f)
        # 确保mypy已经安装
        PackageInstaller.install("mypy")
        # 编译源代码
        execute_python(cls.__PATH, "build_ext", "--build-lib", target_folder)
        # 删除缓存
        cls.__clean_up()
        # 复制额外文件
        cls.copy(additional_files, source_path_in_target_folder)
        # 写入默认的PyInstaller程序
        if include_pyinstaller_program is True:
            PyInstaller.generate(
                os.path.basename(source_folder),
                source_path_in_target_folder,
                builder_options.get("hidden_imports", []),
            )
        # 创建py.typed文件
        with open(os.path.join(source_path_in_target_folder, "py.typed"), "w") as f:
            f.writelines(
                [
                    "Created by linpg-toolbox according to PEP 561.\n",
                    "More information can be found here: https://peps.python.org/pep-0561/\n",
                ]
            )
        # 删除在sitepackages中的旧build，同时复制新的build
        if update_the_one_in_sitepackages is True:
            # 移除旧的build
            PackageInstaller.uninstall(os.path.basename(source_folder))
            # 安装新的build
            PackageInstaller.install(".", user=True)
        # 删除build文件夹
        if remove_building_cache is True:
            cls.remove("build")

    # 构建最新的release
    @classmethod
    def build(cls) -> None:
        # 升级build工具
        PackageInstaller.install("build")
        # 升级wheel工具
        PackageInstaller.install("wheel")
        # 打包文件
        execute_python("-m", "build", "--no-isolation")
        # 根据python_ver以及编译环境重命名
        python_ver: str = f"cp{sys.version_info[0]}{sys.version_info[1]}"
        key_word: str = f"py{sys.version_info[0]}-none-any.whl"
        _evn: str = (
            sysconfig.get_platform().replace("-", "_")
            if sys.platform.startswith("win")
            else "manylinux2014_x86_64"  # PEP 599
            if sys.platform.startswith("linux")
            else "none-any"
        )
        for _wheel_file in glob(os.path.join(cls.__DIST_DIR, f"*-{key_word}")):
            os.rename(
                _wheel_file,
                _wheel_file.replace(
                    key_word,
                    f"{python_ver}-{python_ver}-{_evn}.whl",
                ),
            )

    # 打包上传最新的文件
    @classmethod
    def upload(cls, confirm: bool = True) -> None:
        # 要求用户确认dist文件夹中的打包好的文件之后在继续
        if (
            not confirm
            or input(
                f'Please confirm the files in "{cls.__DIST_DIR}" folder and enter Y to continue:'
            )
            == "Y"
        ):
            # 升级twine
            PackageInstaller.install("twine")
            # 用twine上传文件
            execute_python("-m", "twine", "upload", f"{cls.__DIST_DIR}/*")
        # 删除缓存
        cls.__clean_up()
