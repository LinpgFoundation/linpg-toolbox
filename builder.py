import argparse
from subprocess import check_call

from linpgtoolbox.builder import Builder, execute_python
from linpgtoolbox.organizer import Organizer

# using argparse to parse the argument from command line
parser: argparse.ArgumentParser = argparse.ArgumentParser()
parser.add_argument("-i", help="install cython")
args: argparse.Namespace = parser.parse_args()

# organize the gitignore file
Organizer.organize_gitignore()

# install/upgrade cython (setup environment)
if str(args.i).lower().startswith("t"):
    Builder.remove("./cython")
    check_call(["git", "clone", "https://github.com/cython/cython.git"])
    check_call(["git", "merge", "origin/patma-preview"], cwd="./cython")
    execute_python("-m", "pip", "install", ".", "--upgrade", _cwd="./cython")
    Builder.remove("./cython")

# 需要额外包括的文件
additional_files: tuple[str, ...] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md")

# 编译源代码
Builder.compile(
    "linpgtoolbox",
    additional_files=additional_files,
    ignore_key_words=("_compiler.py",),
    update_the_one_in_sitepackages=True,
    options={
        "enable_multiprocessing": True,
    },
)

# 提示编译完成
for i in range(2):
    print("")
print("--------------------Done!--------------------")
for i in range(2):
    print("")

# 打包上传最新的文件
"""
action: str = input("Do you want to package and upload the latest build (Y/n):")
if action == "Y":
    Builder.build()
    Builder.upload()
elif action != "N":
    Builder.remove("src")
"""
