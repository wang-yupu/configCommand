#
from logging import Logger
from ..fileHandler import json, yaml, toml, plain
import math


class Player:
    fileChangedAndNotSave = False
    fileChangedAndQuitWithoutSave = False

    def __init__(self, playerName: str, fileTarget: str, logger: Logger):
        # 读取
        logger.info(f"尝试读取文件: {fileTarget}")
        self.file = fileTarget

        self.fileContent = None
        self.playerName = playerName
        self.operations = []

        self.currentCursor = '.'

        self.load()

        # 判断文件类型
        fileTypes = {
            ('json',): json.JSONRW,
            ('yaml', 'yml'): yaml.YAMLRW,
            ('toml',): toml.TOMLRW
        }

        RW = plain.PlainTextRW
        for suffixs, tRW in fileTypes.items():
            for suffix in suffixs:
                if fileTarget.endswith(suffix):
                    RW = tRW

        logger.info(f"选择RW: {RW}")

        # 实例化rw
        try:
            self.fileRW = RW()
            self.fileRW.load(self.fileContent)
        except:
            try:
                logger.warning("回落到纯文本...")
                RW = plain.PlainTextRW
                self.fileRW = RW()
                self.fileRW.load(self.fileContent)
            except:
                raise ValueError("纯文本解析失败，也许是插件的问题")

    def write(self):
        try:
            with open(self.file, mode='w') as file:
                file.write(self.fileRW.dump())
        except UnicodeEncodeError as error:
            self.logger.warning("文件UTF-8编码失败")
            raise error
        except PermissionError as error:
            self.logger.warning("文件无权限")
            raise error
        except OSError as error:
            self.logger.warning("系统错误")
            raise error
        except Exception as error:
            self.logger.error(f"未捕获的错误: {error}")
            raise error
        finally:
            self.fileChangedAndNotSave = False
            self.operations.clear()

    def load(self):
        try:
            with open(self.file, 'r', encoding='utf-8') as file:
                self.fileContent = file.read()
        except FileNotFoundError as error:
            self.logger.warning("文件不存在")
            raise error
        except UnicodeDecodeError as error:
            self.logger.warning("文件UTF-8解码失败")
            raise error
        except PermissionError as error:
            self.logger.warning("文件无权限")
            raise error
        except OSError as error:
            self.logger.warning("系统错误")
            raise error
        except Exception as error:
            self.logger.error(f"未捕获的错误: {error}")
            raise error
        finally:
            self.operations.clear()

    def postProcessKey(self, key: str) -> str:
        if key.startswith("/"):
            return key
        if key.startswith("."):
            key.lstrip(".")
        if self.currentCursor != ".":
            return self.currentCursor.rstrip(".") + "." + key
        else:
            return key

    def set(self, key, value: str):
        key = self.postProcessKey(key)

        # 处理数据类型
        r = self.fileRW.getByStringKey(key)
        if isinstance(r, int) and value.isdigit():
            value = int(value)
        elif isinstance(r, bool) and value.upper() in ['TRUE', 'FALSE', 'T', 'F']:
            if value.upper().startswith("T"):
                value = True
            elif value.upper().startswith("F"):
                value = False

        self.fileRW.setByStringKey(key, value)
        self.fileChangedAndNotSave = True
        self.operations.append(f"set {key}: {value}")

    def get(self, key):
        key = self.postProcessKey(key)
        return self.fileRW.getByStringKey(key)

    def ls(self, page):
        r = self.fileRW.toStringTree()
        if page < 1:
            raise ValueError("无效页数")

        itemPerPage = 10
        start = (page - 1) * itemPerPage
        end = start + itemPerPage

        return r[start:end]

    def getPageCount(self) -> int:
        itemPerPage = 10
        return math.ceil(len(self.fileRW.toStringTree())/itemPerPage)

    def rm(self, key):
        key = self.postProcessKey(key)
        self.fileRW.deleteByStringKey(key)
        self.fileChangedAndNotSave = True
        self.operations.append(f"rm {key}")

    def mv(self, source, dest):
        source = self.postProcessKey(source)
        dest = self.postProcessKey(dest)
        self.fileRW.renameKey(source, dest)
        self.fileChangedAndNotSave = True
        self.operations.append(f"mv {source} to {dest}")

    def cp(self, source, dest):
        source = self.postProcessKey(source)
        dest = self.postProcessKey(dest)
        self.fileRW.copyKey(source, dest)
        self.fileChangedAndNotSave = True
        self.operations.append(f"cp {source} to {dest}")
