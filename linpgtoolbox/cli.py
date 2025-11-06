import argparse

from ._execute import set_python_version, sys
from ._fixer import Fixer
from .builder import Builder
from .organizer import Organizer
from .pkginstaller import PackageInstaller


def cli() -> None:
    # create a ArgumentParser for taking argument inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", "-c", type=str, help="Compile project")
    parser.add_argument("--install", "-i", type=str, help="Install project")
    parser.add_argument("--pack", "-p", type=str, help="Pack project")
    parser.add_argument("--upload", type=str, help="Upload packed project to PyPi")
    parser.add_argument(
        "--release", "-r", type=str, help="Pack and upload project to PyPi"
    )
    parser.add_argument("--organize", "-o", type=str, help="Organize project")
    parser.add_argument("--upgrade", type=str, help="Upgrade a pip package")
    parser.add_argument("--zip", type=str, help="Create a source distribution")
    parser.add_argument("--fix", type=str, help="Create a source distribution")
    parser.add_argument("--select-py", type=str, help="Select the python version")
    parser.add_argument(
        "--platform", action="store_true", help="Print current platform information"
    )
    parser.add_argument(
        "--reinstall",
        action="store_true",
        help="Reinstall Linpg Toolbox (Debug Purpose)",
    )

    # get arguments
    args = parser.parse_args()

    # override default python version if given
    if args.select_py:
        set_python_version(args.select_py)

    # eacute operations
    if args.compile:
        Builder.compile(args.compile)
    elif args.install:
        Builder.compile(args.install, upgrade=True)
        Builder.remove("src")
    elif args.zip:
        Builder.zip(args.zip)
    elif args.pack:
        Builder.pack(args.pack)
    elif args.upload:
        Builder.upload(args.upload, False)
    elif args.release:
        Builder.release(args.release)
    elif args.organize:
        Organizer.organize_gitignore(args.organize)
    elif args.upgrade:
        PackageInstaller.upgrade(args.upgrade)
    elif args.fix:
        Fixer.match_case_to_if_else(args.fix)
    elif args.platform:
        print(f"python[{sys.platform}]-{sys.version}")
    elif args.reinstall:
        PackageInstaller.reinstall("linpgtoolbox")


if __name__ == "__main__":
    cli()
