from enum import Enum

from abc import ABC, abstractmethod
import re

from mcdreforged.api.rtext import RText


class HandlerEnum(Enum):
    AUTO = 0

    JSON = 1
    YAML = 2
    TOML = 3
    PLAIN = 4


class TypeEnum(Enum):
    STRING = 0
    INT = 1
    BOOL = 2
    LIST = 3
    OBJECT = 4
    NONE = 5
    AUTO = 6


__all__ = ['BasicRW', 'JSONRW', 'YAMLRW', 'TOMLRW', 'PlainTextRW']


def parse_key(key: str) -> list[str]:
    parts = re.split(r'(?<!\\)\.', key)
    return [p.replace('\\.', '.') for p in parts]


class BasicRW(ABC):
    @property
    @abstractmethod
    def typ(self) -> str: return 'abstract'

    @abstractmethod
    def setByStringKey(self, key, value) -> None: ...

    @abstractmethod
    def getByStringKey(self, key) -> any: ...

    @abstractmethod
    def toStringTree(self) -> list[RText]: ...

    @abstractmethod
    def load(self, rawContent) -> None: ...

    @abstractmethod
    def dump(self) -> str: ...

    @abstractmethod
    def deleteByStringKey(self, key) -> None: ...

    @abstractmethod
    def renameKey(self, oldKey, newKey) -> None: ...

    @abstractmethod
    def copyKey(self, srcKey, destKey) -> None: ...
