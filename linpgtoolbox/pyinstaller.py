import os
import shutil
from typing import Final


class Pyinstaller:

    __FOLDER: Final[str] = "__pyinstaller"

    @classmethod
    def ensure(cls, _name: str) -> None:
        if not os.path.exists(cls.__FOLDER):
            shutil.copytree(
                os.path.join(os.path.dirname(__file__), cls.__FOLDER),
                cls.__FOLDER,
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            hook_path: str = os.path.join(cls.__FOLDER, "hook-{}.py".format(_name))
            os.rename(os.path.join(cls.__FOLDER, "hook.py"), hook_path)
            with open(hook_path, "r", encoding="utf-8") as f:
                lines: list[str] = f.readlines()
            lines[0] = lines[0].removesuffix("\n") + ", " + _name + "\n"
            lines[2] = lines[2].replace('"%path%"', _name + ".__path__[0]")
            lines[3] = lines[3].replace("%name%", _name)
            # 保存数据
            with open(hook_path, "w+", encoding="utf-8") as f:
                f.writelines(lines)
