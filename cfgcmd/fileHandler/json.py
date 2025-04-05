from . import BasicRW, parse_key
import json
import copy


class JSONRW(BasicRW):
    typ = "JSON"

    def __init__(self):
        self.data = {}

    def _traverse(self, key, create=False):
        parts = parse_key(key)
        current = self.data
        path = []

        for part in parts[:-1]:
            path.append((current, part))
            if isinstance(current, dict):
                if part not in current and create:
                    current[part] = {}
                current = current.get(part)
            elif isinstance(current, list):
                index = int(part)
                if index >= len(current) and create:
                    current.extend([{}]*(index - len(current) + 1))
                current = current[index]
            else:
                raise KeyError(f"Invalid path at {part}")
            if current is None:
                raise KeyError(f"Invalid path at {part}")

        return current, parts[-1]

    def setByStringKey(self, key, value) -> None:
        try:
            parent, last = self._traverse(key, create=True)
            if isinstance(parent, dict):
                parent[last] = value
            elif isinstance(parent, list):
                index = int(last)
                if len(parent) == index:
                    parent.append(value)
                else:
                    if index >= len(parent):
                        parent.extend([None]*(index - len(parent) + 1))
                    parent[index] = value
            else:
                raise KeyError("Cannot set value on non-container type")
        except Exception as e:
            raise KeyError(f"Invalid key {key}") from e

    def getByStringKey(self, key) -> any:
        try:
            parent, last = self._traverse(key)
            if isinstance(parent, (dict, list)):
                return parent[last] if isinstance(parent, dict) else parent[int(last)]
            return None
        except:
            return None

    def deleteByStringKey(self, key) -> None:
        try:
            parent, last = self._traverse(key)
            if isinstance(parent, dict):
                del parent[last]
            elif isinstance(parent, list):
                del parent[int(last)]
            else:
                raise KeyError("Cannot delete from non-container type")
        except Exception as e:
            raise KeyError(f"Delete failed: {str(e)}") from e

    def renameKey(self, oldKey, newKey) -> None:
        value = self.getByStringKey(oldKey)
        if value is None:
            raise KeyError(f"Key {oldKey} not found")
        self.deleteByStringKey(oldKey)
        self.setByStringKey(newKey, value)

    def copyKey(self, srcKey, destKey) -> None:
        value = copy.deepcopy(self.getByStringKey(srcKey))
        if value is None:
            raise KeyError(f"Source key {srcKey} not found")
        self.setByStringKey(destKey, value)

    def getValueColored(self, value):
        from ..commands.utils import gray, red, green, blue, white, darkred, bold, RColor
        if value == None:
            return gray('None')
        elif isinstance(value, bool):
            return green("True") if value else red("False")
        elif isinstance(value, int):
            return blue(str(value))
        elif isinstance(value, float):
            integer, fractional = str(value).split(".")
            return blue(integer) + bold(".", RColor.green) + blue(fractional)
        elif isinstance(value, str):
            return darkred(value)
        else:
            try:
                return white(str(value))
            except:
                return red("???")

    def _generate_tree(self, data, prefix='', is_last=False, current_key=''):
        from ..commands.utils import gray, orange, bold, white, RColor
        lines = []
        connector = gray('└── ') if is_last else gray('├── ')
        next_prefix = prefix + gray('    ') if is_last else prefix + gray('│   ')

        if isinstance(data, dict):
            for i, (k, v) in enumerate(data.items()):
                is_last_item = i == len(data)-1
                # 构建当前键路径（处理转义点号）
                escaped_key = str(k).replace('.', '\\.')
                new_key = f"{current_key}.{escaped_key}" if current_key else escaped_key
                key_part = bold(str(k), RColor.gold)

                if isinstance(v, (dict, list)):
                    line = gray(prefix) + connector + key_part
                    # 添加完整键路径到悬浮提示
                    hover_text = f"Object {k}\nPath: {new_key}" if isinstance(v, dict) else f"List {k}\nPath: {new_key}"
                    line.set_hover_text(hover_text)
                    lines.append(line)
                    lines.extend(self._generate_tree(v, next_prefix, is_last_item, new_key))
                else:
                    value_part = white(": ") + self.getValueColored(v)
                    line = gray(prefix) + connector + key_part + value_part
                    line.set_hover_text(f"{type(v).__name__} {k}\nPath: {new_key}")
                    lines.append(line)

        elif isinstance(data, list):
            for i, item in enumerate(data):
                is_last_item = i == len(data)-1
                # 构建列表索引路径
                new_key = f"{current_key}.{i}" if current_key else str(i)
                key_part = orange(white("#")+bold(str(i)))

                if isinstance(item, (dict, list)):
                    line = gray(prefix) + connector + key_part
                    # 添加完整键路径到悬浮提示
                    type_desc = "Object" if isinstance(item, dict) else "List"
                    line.set_hover_text(f"List #{i} ({type_desc})\nPath: {new_key}")
                    lines.append(line)
                    lines.extend(self._generate_tree(item, next_prefix, is_last_item, new_key))
                else:
                    value_part = white(": ") + self.getValueColored(item)
                    line = gray(prefix) + connector + key_part + value_part
                    line.set_hover_text(f"List #{i}: {type(item).__name__}\nPath: {new_key}")
                    lines.append(line)

        return lines

    def toStringTree(self) -> list:
        from ..commands.utils import green, bold, RColor
        header = bold("JSON", RColor.green)
        return [header] + self._generate_tree(self.data) if self.data else [header]

    def load(self, rawContent) -> None:
        self.data = json.loads(rawContent)

    def dump(self) -> str:
        return json.dumps(self.data, indent=2, ensure_ascii=False)
