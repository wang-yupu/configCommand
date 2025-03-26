from . import BasicRW


class PlainTextRW(BasicRW):
    typ = "Plain"

    def __init__(self):
        self.lines = []

    def setByStringKey(self, key, value) -> None:
        try:
            index = int(key) - 1
            if index < 0:
                raise ValueError("Line number must be ≥ 1")
            while index >= len(self.lines):
                self.lines.append('')
            self.lines[index] = str(value)
        except ValueError as e:
            raise KeyError(f"Invalid line number: {key}") from e

    def getByStringKey(self, key) -> any:
        try:
            index = int(key) - 1
            return self.lines[index] if 0 <= index < len(self.lines) else None
        except ValueError as e:
            raise KeyError(f"Invalid line number: {key}") from e

    def deleteByStringKey(self, key) -> None:
        index = int(key) - 1
        if 0 <= index < len(self.lines):
            self.lines[index] = ''
        else:
            raise KeyError(f"Line {key} not found")

    def renameKey(self, oldKey, newKey) -> None:
        old_index = int(oldKey) - 1
        new_index = int(newKey) - 1
        if not 0 <= old_index < len(self.lines):
            raise KeyError(f"Source line {oldKey} not found")

        while new_index >= len(self.lines):
            self.lines.append('')
        self.lines[new_index] = self.lines[old_index]
        self.lines[old_index] = ''

    def copyKey(self, srcKey, destKey) -> None:
        src_index = int(srcKey) - 1
        dest_index = int(destKey) - 1
        if not 0 <= src_index < len(self.lines):
            raise KeyError(f"Source line {srcKey} not found")

        while dest_index >= len(self.lines):
            self.lines.append('')
        self.lines[dest_index] = self.lines[src_index]

    def toStringTree(self) -> list:
        from ..commands.utils import green, bold, gray, white, orange
        header = green(bold("PLAIN"))
        lines = [header]

        for i, line_text in enumerate(self.lines):
            connector = gray('└── ') if i == len(self.lines)-1 else gray('├── ')
            line_no = orange(bold(str(i+1)))
            content = white(f": {line_text}" if line_text else ": <EMPTY>")

            line = connector + line_no + content
            line.set_hover_text(f"行 {i+1}")
            lines.append(line)

        return lines

    def load(self, rawContent) -> None:
        self.lines = rawContent.split('\n')

    def dump(self) -> str:
        return '\n'.join(self.lines)
