from .json import JSONRW
import yaml


class YAMLRW(JSONRW):
    typ = "YAML"

    def load(self, rawContent) -> None:
        self.data = yaml.safe_load(rawContent)

    def dump(self) -> str:
        return yaml.dump(self.data, allow_unicode=True, sort_keys=False)

    def toStringTree(self) -> list:
        from ..commands.utils import green, bold
        header = green(bold("YAML"))
        return [header] + super()._generate_tree(self.data) if self.data else [header]
