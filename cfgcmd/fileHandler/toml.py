from .json import JSONRW
import toml


class TOMLRW(JSONRW):
    def load(self, rawContent) -> None:
        self.data = toml.loads(rawContent)

    def dump(self) -> str:
        return toml.dumps(self.data)

    def toStringTree(self) -> str:
        lines = ["TOML"]
        if self.data:
            lines.extend(self._generate_tree(self.data))
        return '\n'.join(lines)
