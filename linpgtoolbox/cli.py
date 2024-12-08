import argparse

from .builder import Builder


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
    # get arguments
    args = parser.parse_args()
    # eacute operations
    if args.compile:
        Builder.compile(args.compile)
    elif args.install:
        Builder.compile(args.install, upgrade=True)
        Builder.remove("src")
    elif args.pack:
        Builder.pack()
    elif args.upload:
        Builder.upload()
    elif args.release:
        Builder.release()
