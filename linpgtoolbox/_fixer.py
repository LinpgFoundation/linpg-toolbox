import os
import re
from pathlib import Path


class Fixer:

    @classmethod
    def match_case_to_if_else(cls, path: str) -> None:
        if os.path.isdir(path):
            for p in list(Path(path).rglob("*.py")):
                cls.__match_case_to_if_else(str(p))
        else:
            cls.__match_case_to_if_else(path)

    @staticmethod
    def __match_case_to_if_else(input_file: str) -> None:
        # read python script content
        with open(input_file, "r", encoding="utf-8") as f:
            script_content: str = f.read()

        # if not match/case are found, then there is no reason to continue
        if not "match" in script_content or not "case" in script_content:
            return

        # output lines
        converted_lines: list[str] = []
        # indents stack
        indents: list[str] = []
        # match var stack
        match_vars: list[str] = []
        # if hit if and start elif
        hit_if: bool = False

        for line in script_content.splitlines():
            # remove indents in front for better matching
            line_stripped: str = line.strip()
            # get the indents
            line_indent: str = re.match(r"^(\s*)", line).group(1)  # type: ignore

            # if we hit a match
            if line_stripped.startswith("match"):
                # flip the flag to start with if
                hit_if = False
                # capture indentation
                indents.append(line_indent)
                # extract the match variable
                match_vars.append(line_stripped.split(" ")[1].rstrip(":"))
                continue

            # a smaller indent indicates the end of current match block
            if len(indents) > 0 and 0 < len(line_indent) <= len(indents[-1]):
                indents.pop()
                match_vars.pop()

            # if the line is not a case statement, then add the line and continue
            if len(indents) <= 0 or not line_stripped.startswith("case"):
                # Copy other lines unchanged
                converted_lines.append(line)
                continue

            # extract the case condition
            condition: str = line_stripped.split("case")[1].strip().rstrip(":")
            # if condition is _, that indicates a else
            if condition == "_":
                converted_lines.append(f"{indents[-1]}else:")
            else:
                condition = (
                    f"in ({','.join(condition.split('|'))})"
                    if "|" in condition
                    else f"== {condition}"
                )
                # First case becomes 'if', others become 'elif'
                if not hit_if:
                    converted_lines.append(
                        f"{indents[-1]}if {match_vars[-1]} {condition}:"
                    )
                    hit_if = True
                else:
                    converted_lines.append(
                        f"{indents[-1]}elif {match_vars[-1]} {condition}:"
                    )

        # write the modified python script content back
        with open(input_file, "w", encoding="utf-8") as f:
            f.write("\n".join(converted_lines))
