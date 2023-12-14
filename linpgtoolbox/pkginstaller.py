import importlib.metadata

from ._execute import execute_python


class PackageInstaller:
    # 安装（第三方）库
    @classmethod
    def install(
        cls,
        pkg_name: str,
        upgrade: bool = True,
        user: bool = False,
        cwd: str | None = None,
    ) -> None:
        _cmd: list[str] = ["-m", "pip", "install", pkg_name]
        # 确保安装最新的版本
        if upgrade is True:
            _cmd.append("--upgrade")
        # 只为用户安装
        if user is True:
            _cmd.append("--user")
        execute_python(*_cmd, cwd=cwd)

    # 卸载（第三方）库
    @classmethod
    def uninstall(cls, pkg_name: str) -> None:
        execute_python("-m", "pip", "uninstall", "-y", pkg_name)

    # 升级所有（第三方）库
    @classmethod
    def upgrade(cls, name: str = "*") -> None:
        if name == "*":
            for distribution in importlib.metadata.distributions():
                name = distribution.metadata["Name"]
                if not name.startswith("_"):
                    try:
                        cls.install(name)
                    except Exception:
                        print(f"Warning: fail to update third party package <{name}>")
        else:
            cls.install(name)
