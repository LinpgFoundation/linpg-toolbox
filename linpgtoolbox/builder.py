import os
import re
import shutil
import sys
import sysconfig
import tomllib
from collections import deque
from glob import glob
from json import dump
from subprocess import check_call
from tempfile import gettempdir
from typing import Any, Final

from ._execute import execute_python
from .pyinstaller import PackageInstaller, PyInstaller


# 搭建和打包文件的系统
class Builder:
    __PATH: Final[str] = os.path.join(os.path.dirname(__file__), "_compiler.py")
    __CACHE_NEED_REMOVE: Final[tuple[str, ...]] = (
        "dist",
        "Save",
        "build",
        "crash_reports",
        "Cache",
    )
    CACHE_NEED_REMOVE: Final[deque[str]] = deque()
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
    def remove(*path: str, cwd: str | None = None) -> None:
        for _path in path:
            if cwd is not None:
                _path = os.path.join(cwd, _path)
            if os.path.exists(_path):
                shutil.rmtree(_path) if os.path.isdir(_path) else os.remove(_path)

    # 复制文件
    @classmethod
    def copy(
        cls, files: tuple[str, ...], target_folder: str, move: bool = False
    ) -> None:
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
            if move:
                cls.remove(the_file)

    # 复制文件夹
    @classmethod
    def copy_tree(
        cls, src: str, dest: str, move: bool = False, ignore_pattern: str = ""
    ) -> None:
        if not os.path.exists(dest):
            os.makedirs(dest)
        for item in os.listdir(src):
            s: str = os.path.join(src, item)
            if ignore_pattern and re.search(ignore_pattern, s):
                continue
            d: str = os.path.join(dest, item)
            if os.path.isdir(s):
                cls.copy_tree(s, d, move, ignore_pattern)
            else:
                shutil.copy(s, d)
            if move:
                cls.remove(s)

    # 复制Repo
    @classmethod
    def copy_repo(cls, src: str, dest: str, move: bool = False) -> None:
        cls.copy_tree(src, dest, move, ".*.git$")

    # 删除缓存
    @classmethod
    def __clean_up(cls) -> None:
        cls.remove(*cls.__CACHE_NEED_REMOVE)

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
        remove_build_cache: bool = True,
        upgrade: bool = False,
        show_success_message: bool = True,
    ) -> None:
        # make sure required libraries are installed
        PackageInstaller.install("setuptools")
        PackageInstaller.install("cython")
        # 移除cache
        cls.remove(target_folder)
        # 复制文件到新建的src文件夹中，准备开始编译
        os.makedirs(target_folder)
        source_path_in_target_folder: str = os.path.join(
            target_folder, os.path.basename(source_folder)
        )
        cls.copy_repo(source_folder, source_path_in_target_folder)
        # load config for linpgtoolbox
        pyproject_path: Final[str] = os.path.join(
            os.path.dirname(source_folder), "pyproject.toml"
        )
        _config: dict[str, Any] = {}
        _options: dict[str, Any] = {}
        if os.path.exists(pyproject_path):
            with open(pyproject_path, "rb") as f:
                _config.update(tomllib.load(f).get("tool", {}).get("linpgtoolbox", {}))
                _options.update(_config.get("options", {}))
        # 移除不必要的py缓存
        cls.__remove_cache(target_folder)
        # 如果开启了智能模块合并模式
        smart_auto_module_combine: str = _options.get(
            "smart_auto_module_combine", "disable"
        )
        if smart_auto_module_combine != "disable":
            for _path in glob(os.path.join(source_path_in_target_folder, "*")):
                cls.__combine(_path)
        if smart_auto_module_combine == "all_in_one":
            cls.__combine(source_path_in_target_folder)
        # 如果目标文件夹有cmake文件
        if (
            os.path.exists(
                CMakeListsFilePath := os.path.join(
                    source_path_in_target_folder, "CMakeLists.txt"
                )
            )
            and _options.get("auto_cmake", False) is True
        ):
            # create a temporary build folder
            cmake_build_dir: Final[str] = os.path.join(
                source_path_in_target_folder, "build"
            )
            cls.remove(cmake_build_dir)
            os.makedirs(cmake_build_dir)
            # make project
            check_call(["cmake", ".."], cwd=cmake_build_dir)
            check_call(
                ["cmake", "--build", ".", "--config", "Release"], cwd=cmake_build_dir
            )
            # copy compiled python files (windows)
            cls.copy(
                tuple(glob(os.path.join(cmake_build_dir, "Release", "*.pyd"))),
                source_path_in_target_folder,
            )
            # copy compiled python files (linux)
            cls.copy(
                tuple(glob(os.path.join(cmake_build_dir, "*.so"))),
                source_path_in_target_folder,
            )
            cls.remove(cmake_build_dir)
            cls.remove(CMakeListsFilePath)
        # 把数据写入缓存文件以供编译器读取
        builder_options: dict[str, Any] = {
            "source_folder": source_path_in_target_folder,
            "ignores": _config.get("ignores", tuple()),
            "enable_multiprocessing": True,
            "debug_mode": False,
            "emit_code_comments": False,
            "keep_c": False,
            "compiler_directives": {},
        }
        builder_options.update(_options)
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
        # remove include files
        for included_path in _config.get("includes", tuple()):
            cls.remove(
                os.path.join(
                    source_path_in_target_folder, os.path.basename(included_path)
                )
            )
        # 删除缓存
        cls.__clean_up()
        cls.remove(*cls.CACHE_NEED_REMOVE, cwd=source_path_in_target_folder)
        # 复制额外文件
        cls.copy(tuple(_config.get("includes", tuple())), source_path_in_target_folder)
        # 写入默认的PyInstaller程序
        if _config.get("include_pyinstaller", False) is True:
            PyInstaller.generate_hook(
                os.path.basename(source_folder),
                source_path_in_target_folder,
                builder_options.get("hidden_imports", []),
            )
        # 创建py.typed文件
        with open(
            os.path.join(
                (
                    source_path_in_target_folder
                    if os.path.exists(source_path_in_target_folder)
                    else target_folder
                ),
                "py.typed",
            ),
            "w",
        ) as f:
            f.writelines(
                (
                    "Created by linpg-toolbox according to PEP 561.\n",
                    "More information can be found here: https://peps.python.org/pep-0561/\n",
                )
            )
        # 删除在sitepackages中的旧build，同时复制新的build
        if upgrade is True:
            # 移除旧的build
            PackageInstaller.uninstall(os.path.basename(source_folder))
            # 安装新的build
            PackageInstaller.install(".")
        # 删除build文件夹
        if remove_build_cache is True:
            cls.remove("build")
        # 提示编译完成
        if show_success_message:
            for _ in range(2):
                print("")
            print("--------------------Done!--------------------")
            for _ in range(2):
                print("")

    # 构建最新的release
    @classmethod
    def pack(cls) -> None:
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
            else (
                "manylinux2014_x86_64"  # PEP 599
                if sys.platform.startswith("linux")
                else "none-any"
            )
        )
        for _wheel_file in glob(os.path.join(cls.__DIST_DIR, f"*-{key_word}")):
            os.rename(
                _wheel_file,
                _wheel_file.replace(
                    key_word,
                    f"{python_ver}-{python_ver}-{_evn}.whl",
                ),
            )

    # upload the packaged project
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

    # pack and upload project
    @classmethod
    def release(cls, confirm: bool = True) -> None:
        cls.pack()
        cls.upload(confirm)
