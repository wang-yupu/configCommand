from . import BasicRW, parse_key
import json
import copy


class JSONRW(BasicRW):
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

    def _generate_tree(self, data, prefix='', is_last=False):
        lines = []
        if isinstance(data, dict):
            items = list(data.items())
            for i, (k, v) in enumerate(items):
                new_prefix = prefix + ('└ ' if (i == len(items)-1 and is_last) else '├ ')
                if i == len(items)-1:
                    new_prefix = prefix + '└ '
                else:
                    new_prefix = prefix + '├ '
                if isinstance(v, dict):
                    lines.append(f"{new_prefix}Object {k}")
                    child_prefix = prefix + ('    ' if (i == len(items)-1) else '│   ')
                    lines.extend(self._generate_tree(v, child_prefix, i == len(items)-1))
                elif isinstance(v, list):
                    lines.append(f"{new_prefix}List {k}")
                    child_prefix = prefix + ('    ' if (i == len(items)-1) else '│   ')
                    lines.extend(self._generate_tree(v, child_prefix, i == len(items)-1))
                else:
                    lines.append(f"{new_prefix}{type(v).__name__} {k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_prefix = prefix + ('└ ' if (i == len(data)-1 and is_last) else '├ ')
                if isinstance(item, dict):
                    lines.append(f"{new_prefix}List # {i} (Object)")
                    child_prefix = prefix + ('    ' if (i == len(data)-1) else '│   ')
                    lines.extend(self._generate_tree(item, child_prefix, i == len(data)-1))
                elif isinstance(item, list):
                    lines.append(f"{new_prefix}List # {i} (List)")
                    child_prefix = prefix + ('    ' if (i == len(data)-1) else '│   ')
                    lines.extend(self._generate_tree(item, child_prefix, i == len(data)-1))
                else:
                    lines.append(f"{new_prefix}List # {i}: {type(item).__name__} {item}")
        return lines

    def toStringTree(self) -> str:
        lines = ["JSON"]
        if self.data:
            lines.extend(self._generate_tree(self.data))
        return '\n'.join(lines)

    def load(self, rawContent) -> None:
        self.data = json.loads(rawContent)

    def dump(self) -> str:
        return json.dumps(self.data, indent=2, ensure_ascii=False)
