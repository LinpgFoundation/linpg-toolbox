import argparse
import os
import tomllib

from .builder import Builder
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

    # get arguments
    args = parser.parse_args()
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


if __name__ == "__main__":
    cli()
