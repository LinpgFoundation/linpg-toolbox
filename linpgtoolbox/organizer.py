# 整理功能模块
class Organizer:

    # 整理gitignore
    @staticmethod
    def organize_gitignore(_path: str = ".gitignore") -> None:
        if _path.endswith(".gitignore"):
            # 读取列表
            with open(_path, "r", encoding="utf-8") as f:
                lines: list[str] = f.readlines()
            # 确保最后一行一定有换行符号，之后便不在需要手动插入
            if not lines[-1].endswith("\n"):
                lines[-1] += "\n"
            # 把列表进行归类
            sections: dict[str, list[str]] = {"default": []}
            current_key: str = "default"
            for _line in lines:
                if _line.startswith("#"):
                    current_key = _line
                    sections[current_key] = []
                elif len(_line.removesuffix("\n")) > 0:
                    sections[current_key].append(_line)
            # 处理默认数据
            result_lines: list[str] = (
                sorted(sections["default"]) if len(sections["default"]) > 0 else []
            )
            sections.pop("default")
            # 如果有其他的类别，则需要依次处理
            for key, value in sections.items():
                if len(value) > 0:
                    result_lines.append("\n")
                    result_lines.append(key)
                    result_lines.extend(sorted(value))
            # 保存数据
            with open(_path, "w+", encoding="utf-8") as f:
                f.writelines(result_lines)
        else:
            raise FileNotFoundError("The file has to be gitignore!")
