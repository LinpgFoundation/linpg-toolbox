import os
import shutil
from subprocess import check_call
from typing import Final

from .pkginstaller import PackageInstaller


class PyInstaller:
    __FOLDER: Final[str] = "__pyinstaller"

    @classmethod
    def generate_hook(cls, _name: str, _path: str, _hidden_imports: list[str]) -> None:
        # 确定目标__pyinstaller存放目录
        _path = os.path.join(_path, cls.__FOLDER)
        # 删除旧的目录
        if os.path.exists(_path):
            shutil.rmtree(_path)
        # 复制模板文件
        shutil.copytree(
            os.path.join(os.path.dirname(__file__), cls.__FOLDER),
            _path,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        # 重命名hook.py文件
        hook_path: str = os.path.join(_path, f"hook-{_name}.py")
        os.rename(os.path.join(_path, "hook.py"), hook_path)
        # 读取数据
        with open(hook_path, "r", encoding="utf-8") as f:
            lines: list[str] = f.readlines()
        # 生成自定义数据
        lines[0] = lines[0].removesuffix("\n") + ", " + _name + "\n"
        lines[2] = lines[2].replace('"%path%"', _name + ".__path__[0]")
        lines[3] = lines[3].replace("%name%", _name)
        if len(_hidden_imports) > 0:
            lines[5] = f"hiddenimports = {_hidden_imports}\n"
        # 写入数据
        with open(hook_path, "w+", encoding="utf-8") as f:
            f.writelines(lines)

    # pack a project
    @staticmethod
    def pack(spec_path: str) -> None:
        # make sure pyinstaller is installed
        PackageInstaller.install("pyinstaller")
        # pack the project
        check_call(["pyinstaller", spec_path])
