import pkg_resources

from ._execute import execute_python


class PackageInstaller:
    # 安装（第三方）库
    @classmethod
    def install(cls, pkg_name: str, upgrade: bool = True, user: bool = False) -> None:
        _cmd: list[str] = ["-m", "pip", "install", pkg_name]
        # 尝试安装最新的版本
        if upgrade is True:
            _cmd.append("--upgrade")
        # 只为用户安装
        if user is True:
            _cmd.append("--user")
        execute_python(*_cmd)

    # 卸载（第三方）库
    @classmethod
    def uninstall(cls, pkg_name: str) -> None:
        execute_python("-m", "pip", "uninstall", pkg_name)

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
