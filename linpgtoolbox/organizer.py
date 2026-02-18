import fnmatch
import json
import os
from typing import Any


class Organizer:

    # parse gitignore file and return a list of patterns
    @staticmethod
    def _parse_gitignore(gitignore_path: str) -> list[str]:
        patterns: list[str] = []
        if not os.path.isfile(gitignore_path):
            return patterns
        with open(gitignore_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                # skip empty lines and comments
                if line and not line.startswith("#"):
                    patterns.append(line)
        return patterns

    # check if a path should be ignored based on gitignore patterns
    @staticmethod
    def _is_ignored(
        name: str, rel_path: str, is_dir: bool, patterns: list[str]
    ) -> bool:
        for pattern in patterns:
            # strip trailing slash for matching, but remember if it's dir-only
            dir_only: bool = pattern.endswith("/")
            p: str = pattern.rstrip("/")
            if dir_only and not is_dir:
                continue
            # match against both the name and relative path
            if fnmatch.fnmatch(name, p) or fnmatch.fnmatch(rel_path, p):
                return True
        return False

    # organize file or directory
    @staticmethod
    def organize(path: str) -> None:
        # if path is a file, organize it directly
        if os.path.isfile(path):
            if path.endswith(".json"):
                Organizer.organize_json_file(path)
            elif path.endswith(".gitignore"):
                Organizer.organize_gitignore(path)
        # if path is a directory, iterate through all files
        elif os.path.isdir(path):
            # parse gitignore patterns from the root directory
            gitignore_patterns: list[str] = Organizer._parse_gitignore(
                os.path.join(path, ".gitignore")
            )
            for root, dirs, files in os.walk(path):
                # filter out ignored directories (modify in-place to prevent os.walk from descending)
                dirs[:] = [
                    d
                    for d in dirs
                    if not Organizer._is_ignored(
                        d,
                        os.path.relpath(os.path.join(root, d), path),
                        True,
                        gitignore_patterns,
                    )
                ]
                for f in files:
                    file_path: str = os.path.join(root, f)
                    rel_path: str = os.path.relpath(file_path, path)
                    # skip files that match gitignore patterns
                    if Organizer._is_ignored(f, rel_path, False, gitignore_patterns):
                        continue
                    if f.endswith(".json"):
                        Organizer.organize_json_file(file_path)
                    elif f == ".gitignore":
                        Organizer.organize_gitignore(file_path)

    # organize json file
    @staticmethod
    def organize_json_file(filePath: str) -> None:
        # read content from json file
        with open(filePath, "r", encoding="utf-8") as f:
            data: Any = json.load(f)
        # write the data back to json file
        with open(filePath, "w+", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False, sort_keys=True)
        # print confirmation message
        print(f"Organized JSON file: {filePath}")

    # organize gitignore
    @staticmethod
    def organize_gitignore(filePath: str) -> None:
        # check if target file is a gitignore file
        if not filePath.endswith(".gitignore"):
            print("The file has to be gitignore!")
            return
        # read content from gitignore file
        with open(filePath, "r", encoding="utf-8") as f:
            lines: list[str] = f.readlines()
        # making sure that the last line has \n symbol.
        # if not, then add one right now
        if not lines[-1].endswith("\n"):
            lines[-1] += "\n"
        # organize the list into different group
        sections: dict[str, list[str]] = {"default": []}
        current_key: str = "default"
        for _line in lines:
            if _line.startswith("#"):
                current_key = _line
                sections[current_key] = []
            elif len(_line.removesuffix("\n")) > 0:
                sections[current_key].append(_line)
        # processing default data first
        result_lines: list[str] = (
            sorted(sections["default"]) if len(sections["default"]) > 0 else []
        )
        sections.pop("default")
        # If there are other categories, they need to be handled in turn
        for key, value in sections.items():
            if len(value) > 0:
                result_lines.append("\n")
                result_lines.append(key)
                result_lines.extend(sorted(value))
        # write the data back to gitignore file
        with open(filePath, "w+", encoding="utf-8") as f:
            f.writelines(result_lines)

        # print confirmation message
        print(f"Organized .gitignore file: {filePath}")
