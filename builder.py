from linpgtoolbox.builder import Builder, PackageInstaller
from linpgtoolbox.organizer import Organizer

# organize the gitignore file
# Organizer.organize_gitignore()

# install/upgrade cython (setup environment)
PackageInstaller.install("cython")

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
# Builder.build()
# Builder.upload()
Builder.remove("src")
