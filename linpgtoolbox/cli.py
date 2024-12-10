import argparse
import os
import tomllib

from .builder import Builder
from .organizer import Organizer


def _get_project_name(path: str) -> str:
    if path != ".":
        return path
    if not os.path.exists("pyproject.toml"):
        raise FileNotFoundError("Cannot find pyproject.toml!")
    with open("pyproject.toml", "rb") as f:
        return tomllib.load(f)["project"]["name"]


def cli() -> None:
    # create a ArgumentParser for taking argument inputs
    parser = argparse.ArgumentParser()
    parser.add_argument("--compile", "-c", type=str, help="Compile project")
    parser.add_argument("--install", "-i", type=str, help="Install project")
    parser.add_argument("--pack", "-p", type=str, help="Pack project")
    parser.add_argument(
        "--upload", "-u", type=str, help="Upload packed project to PyPi"
    )
    parser.add_argument(
        "--release", "-r", type=str, help="Pack and upload project to PyPi"
    )
    parser.add_argument("--organize", "-o", type=str, help="Organize project")
    # get arguments
    args = parser.parse_args()
    # eacute operations
    if args.compile:
        Builder.compile(_get_project_name(args.compile))
    elif args.install:
        Builder.compile(_get_project_name(args.install), upgrade=True)
        Builder.remove("src")
    elif args.pack:
        Builder.pack()
    elif args.upload:
        Builder.upload()
    elif args.release:
        Builder.release()
    elif args.organize:
        Organizer.organize_gitignore(args.organize)
