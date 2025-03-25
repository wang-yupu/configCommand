from .json import JSONRW
import yaml


class YAMLRW(JSONRW):
    def load(self, rawContent) -> None:
        self.data = yaml.safe_load(rawContent)

    def dump(self) -> str:
        return yaml.dump(self.data, allow_unicode=True, sort_keys=False)

    def toStringTree(self) -> str:
        lines = ["YAML"]
        if self.data:
            lines.extend(self._generate_tree(self.data))
        return '\n'.join(lines)
