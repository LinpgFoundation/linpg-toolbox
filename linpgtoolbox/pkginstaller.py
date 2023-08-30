import sys
from subprocess import check_call
from typing import Final

import pkg_resources


class PackageInstaller:
    PYTHON_PREFIX: Final[str] = (
        "python" if sys.platform.startswith("win") else f"python3.{sys.version_info[1]}"
    )

    # 安装（第三方）库
    @classmethod
    def install(cls, pkg_name: str, upgrade: bool = True, user: bool = False) -> None:
        _cmd: list[str] = [cls.PYTHON_PREFIX, "-m", "pip", "install", pkg_name]
        # 尝试安装最新的版本
        if upgrade is True:
            _cmd.append("--upgrade")
        # 只为用户安装
        if user is True:
            _cmd.append("--user")
        check_call(_cmd)

    # 卸载（第三方）库
    @classmethod
    def uninstall(cls, pkg_name: str) -> None:
        check_call([cls.PYTHON_PREFIX, "-m", "pip", "uninstall", pkg_name])

    # 升级所有（第三方）库
    @classmethod
    def upgrade_all(cls) -> None:
        for pkg in pkg_resources.working_set:
            try:
                cls.install(pkg.project_name)
            except Exception:
                print(
                    f"Warning: fail to update third party package <{pkg.project_name}>"
                )
