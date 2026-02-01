import json
import os
from typing import Any


class Organizer:

    # organize directory
    @staticmethod
    def organize_directory(directoryPath: str) -> None:
        # iterate through all files in the directory
        for root, _, files in os.walk(directoryPath):
            for f in files:
                file_path: str = os.path.join(root, f)
                # organize json files
                if f.endswith(".json"):
                    Organizer.organize_json_file(file_path)
                # organize gitignore files
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
