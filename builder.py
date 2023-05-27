from os import path as PATH

from linpgtoolbox.builder import Builder
from linpgtoolbox.organizer import Organizer

# 整理gitignore文件
# Organizer.organize_gitignore()

# 需要额外包括的文件
additional_files: tuple[str, ...] = ("README.md", "LICENSE", "CODE_OF_CONDUCT.md")

# 编译源代码
Builder.compile(
    "linpgtoolbox",
    additional_files=additional_files,
    ignore_key_words=("compiler.py",),
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
    Builder.upload_package("cp310")
elif action != "N":
    Builder.delete_file_if_exist("src")
"""