import os

_PATH: str = "%path%"
_NAME: str = "%name%"

# no hidden import

datas: list[tuple[str, str]] = []
ignores: tuple[str, ...] = ("__pyinstaller", "__pycache__", ".git")


# check if no ignore key appear in the given file name
def _does_not_match_any_ignores(_file_name: str) -> bool:
    for folder_name_t in ignores:
        if folder_name_t in _file_name:
            return False
    return True


# append all files/folders into datas
for file_name in os.listdir(_PATH):
    # append all folders into datas
    if os.path.isdir(os.path.join(_PATH, file_name)):
        if _does_not_match_any_ignores(file_name):
            datas.append(
                (os.path.join(_PATH, file_name), os.path.join(_NAME, file_name))
            )
    # append all file (except gitignore) into datas
    elif "gitignore" not in file_name:
        datas.append((os.path.join(_PATH, file_name), os.path.join(_NAME)))
