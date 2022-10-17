import os

__PATH: str = "%path%"
__NAME: str = "%name%"

files: list[tuple[str, str]] = []
ignores: tuple[str, ...] = ("__pyinstaller", "__pycache__", ".git")

for file_name in os.listdir(__PATH):
    # 文件夹
    if os.path.isdir(os.path.join(__PATH, file_name)):
        ignore_this_folder: bool = False
        for folder_name_t in ignores:
            if folder_name_t in file_name:
                ignore_this_folder = True
                break
        if not ignore_this_folder:
            files.append(
                (
                    os.path.join(__PATH, file_name),
                    os.path.join(__NAME, file_name),
                )
            )
    # 文件
    elif "gitignore" not in file_name:
        files.append((os.path.join(__PATH, file_name), os.path.join(__NAME)))
