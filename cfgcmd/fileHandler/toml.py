from .json import JSONRW
import toml


class TOMLRW(JSONRW):
    typ = "TOML"

    def load(self, rawContent) -> None:
        self.data = toml.loads(rawContent)

    def dump(self) -> str:
        return toml.dumps(self.data)

    def toStringTree(self) -> list:
        from ..commands.utils import green, bold
        header = green(bold("TOML"))
        return [header] + super()._generate_tree(self.data) if self.data else [header]
