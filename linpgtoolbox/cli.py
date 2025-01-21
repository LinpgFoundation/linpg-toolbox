import argparse
import os

from ._execute import set_python_version, sys
from ._fixer import Fixer
from .builder import Builder, tomllib
from .organizer import Organizer
from .pkginstaller import PackageInstaller


def _get_project_name(path: str) -> str:
    if path != ".":
        return path
    if not os.path.exists("pyproject.toml"):
        raise FileNotFoundError("Cannot find pyproject.toml!")
    with open("pyproject.toml", "rb") as f:
        return str(tomllib.load(f)["project"]["name"])


def cli() -> None:
    # create a ArgumentParser for taking argument inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", "-c", type=str, help="Compile project")
    parser.add_argument("--install", "-i", type=str, help="Install project")
    parser.add_argument("--pack", "-p", action="store_true", help="Pack project")
    parser.add_argument(
        "--upload", action="store_true", help="Upload packed project to PyPi"
    )
    parser.add_argument(
        "--release", "-r", action="store_true", help="Pack and upload project to PyPi"
    )
    parser.add_argument("--organize", "-o", type=str, help="Organize project")
    parser.add_argument("--upgrade", type=str, help="Upgrade a pip package")
    parser.add_argument("--zip", type=str, help="Create a source distribution")
    parser.add_argument("--build-all", type=str, help="Create a source distribution")
    parser.add_argument("--fix", type=str, help="Create a source distribution")
    parser.add_argument("--select-py", type=str, help="Select the python version")
    parser.add_argument(
        "--platform", action="store_true", help="Print current platform information"
    )

    # get arguments
    args = parser.parse_args()

    # override default python version if given
    if args.select_py:
        set_python_version(args.select_py)

    # eacute operations
    if args.compile:
        Builder.compile(_get_project_name(args.compile))
    elif args.install:
        Builder.compile(_get_project_name(args.install), upgrade=True)
        Builder.remove("src")
    elif args.build_all:
        Builder.build_all(_get_project_name(args.build_all))
    elif args.zip:
        Builder.compile(_get_project_name(args.zip), skip_compile=True)
        Builder.pack(False)
    elif args.pack:
        Builder.pack()
    elif args.upload:
        Builder.upload(False)
    elif args.release:
        Builder.release()
    elif args.organize:
        Organizer.organize_gitignore(args.organize)
    elif args.upgrade:
        PackageInstaller.upgrade(args.upgrade)
    elif args.fix:
        Fixer.match_case_to_if_else(args.fix)
    elif args.platform:
        print(sys.platform, sys.version)


if __name__ == "__main__":
    cli()
