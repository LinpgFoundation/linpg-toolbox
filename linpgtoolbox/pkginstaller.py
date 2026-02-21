import importlib.metadata
import json
import urllib.request

from ._execute import execute_python


class PackageInstaller:

    # run pip commend
    @staticmethod
    def pip(*cmd: str, cwd: str | None = None) -> None:
        execute_python("-m", "pip", *cmd, cwd=cwd)

    # install a third-party library
    @classmethod
    def install(
        cls, pkg_name: str, upgrade: bool = True, cwd: str | None = None
    ) -> None:
        _cmd: list[str] = ["install", pkg_name]
        # ensure the latest version will be installed
        if upgrade is True:
            _cmd.append("--upgrade")
        cls.pip(*_cmd, cwd=cwd)

    # uninstall a third-party library
    @classmethod
    def uninstall(cls, pkg_name: str) -> None:
        cls.pip("uninstall", "-y", pkg_name)

    # reinstall a third-party library
    @classmethod
    def reinstall(cls, pkg_name: str) -> None:
        cls.uninstall(pkg_name)
        cls.install(pkg_name)

    # upgrade a third-party library (* for upgrading all third-party libraries)
    @classmethod
    def upgrade(cls, name: str = "*") -> None:
        # only upgrade given third-party library
        if name != "*":
            cls.install(name)
            return
        # upgrade all third-party libraries
        for distribution in importlib.metadata.distributions():
            name = distribution.metadata["Name"]
            if not name.startswith("_"):
                try:
                    cls.install(name)
                except Exception:
                    print(f"Warning: fail to update third party package <{name}>")

    # get the currently installed version of linpgtoolbox
    @staticmethod
    def get_current_version() -> str:
        return importlib.metadata.version("linpgtoolbox")

    # check if a newer version is available on PyPI and offer to update
    @classmethod
    def check_for_update(cls) -> None:
        pkg_name: str = "linpgtoolbox"
        current: str = cls.get_current_version()
        print(f"Current version: {current}")
        try:
            with urllib.request.urlopen(
                f"https://pypi.org/pypi/{pkg_name}/json", timeout=10
            ) as response:
                latest: str = json.loads(response.read())["info"]["version"]
        except Exception:
            print("Failed to fetch latest version from PyPI.")
            return
        print(f"Latest version:  {latest}")
        current_parts: tuple[int, ...] = tuple(int(x) for x in current.split("."))
        latest_parts: tuple[int, ...] = tuple(int(x) for x in latest.split("."))
        if current_parts >= latest_parts:
            print("linpgtoolbox is up to date.")
        else:
            answer: str = input(
                f"A newer version ({latest}) is available. Update now? [y/N] "
            )
            if answer.strip().lower() in ("y", "yes"):
                cls.install(pkg_name)
            else:
                print("Update skipped.")
