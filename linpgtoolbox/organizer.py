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
    @classmethod
    def organize(cls, path: str) -> None:
        changed: int = 0
        unchanged: int = 0
        # if path is a file, organize it directly
        if os.path.isfile(path):
            if path.endswith(".json"):
                if cls.organize_json_file(path):
                    changed += 1
                else:
                    unchanged += 1
            elif path.endswith(".gitignore"):
                if cls.organize_gitignore(path):
                    changed += 1
                else:
                    unchanged += 1
        # if path is a directory, iterate through all files
        elif os.path.isdir(path):
            # parse gitignore patterns from the root directory
            gitignore_patterns: list[str] = cls._parse_gitignore(
                os.path.join(path, ".gitignore")
            )
            for root, dirs, files in os.walk(path):
                # filter out ignored directories (modify in-place to prevent os.walk from descending)
                dirs[:] = [
                    d
                    for d in dirs
                    if not cls._is_ignored(
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
                    if cls._is_ignored(f, rel_path, False, gitignore_patterns):
                        continue
                    result: bool = False
                    if f.endswith(".json"):
                        result = cls.organize_json_file(file_path)
                    elif f == ".gitignore":
                        result = cls.organize_gitignore(file_path)
                    else:
                        continue
                    if result:
                        changed += 1
                    else:
                        unchanged += 1
        # print summary
        if changed == 0 and unchanged == 0:
            print("No supported files found.")
        elif changed == 0:
            print(f"{unchanged} file{'s' if unchanged != 1 else ''} left unchanged.")
        elif unchanged == 0:
            print(f"{changed} file{'s' if changed != 1 else ''} organized.")
        else:
            print(
                f"{changed} file{'s' if changed != 1 else ''} organized,"
                f" {unchanged} file{'s' if unchanged != 1 else ''} left unchanged."
            )

    # organize json file, return True if content changed
    @staticmethod
    def organize_json_file(filePath: str) -> bool:
        # read original content
        with open(filePath, "r", encoding="utf-8") as f:
            original: str = f.read()
        # generate organized content
        data: Any = json.loads(original)
        organized: str = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
        # only write if content changed
        if original != organized:
            with open(filePath, "w+", encoding="utf-8") as f:
                f.write(organized)
            print(f"Organized JSON file: {filePath}")
            return True
        return False

    # organize gitignore, return True if content changed
    @staticmethod
    def organize_gitignore(filePath: str) -> bool:
        # check if target file is a gitignore file
        if not filePath.endswith(".gitignore"):
            print("The file has to be gitignore!")
            return False
        # read content from gitignore file
        with open(filePath, "r", encoding="utf-8") as f:
            original: str = f.read()
        lines: list[str] = original.splitlines(keepends=True)
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
        # only write if content changed
        organized: str = "".join(result_lines)
        if original != organized:
            with open(filePath, "w+", encoding="utf-8") as f:
                f.write(organized)
            print(f"Organized .gitignore file: {filePath}")
            return True
        return False
