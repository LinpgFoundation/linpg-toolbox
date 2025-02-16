import os


class Organizer:
    # organize gitignore
    @staticmethod
    def organize_gitignore(_dir: str = ".", filename: str = ".gitignore") -> None:
        # join path
        _dir = os.path.join(_dir, filename)
        # check if target file is a gitignore file
        if not _dir.endswith(".gitignore"):
            raise FileNotFoundError("The file has to be gitignore!")
        # read content from gitignore file
        with open(_dir, "r", encoding="utf-8") as f:
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
        with open(_dir, "w+", encoding="utf-8") as f:
            f.writelines(result_lines)
