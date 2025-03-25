#
from logging import Logger
import os.path
from ..fileHandler import json, yaml, toml, plain


class Player:
    fileChangedAndNotSave = False
    fileChangedAndQuitWithoutSave = False

    def __init__(self, playerName: str, fileTarget: str, logger: Logger):
        # 读取
        logger.info(f"尝试读取文件: {fileTarget}")
        self.file = fileTarget

        self.fileContent = None
        self.playerName = playerName
        try:
            with open(fileTarget, 'r', encoding='utf-8') as file:
                self.fileContent = file.read()
        except FileNotFoundError as error:
            logger.warning("文件不存在")
            raise error
        except UnicodeDecodeError as error:
            logger.warning("文件UTF-8解码失败")
            raise error
        except PermissionError as error:
            logger.warning("文件无权限")
            raise error
        except OSError as error:
            logger.warning("系统错误")
            raise error
        except Exception as error:
            logger.error(f"未捕获的错误: {error}")
            raise error

        # 判断文件类型
        fileTypes = {
            ['json']: json.JSONRW,
            ['yaml', 'yml']: yaml.YAMLRW,
            ['toml']: toml.TOMLRW
        }

        RW = plain.PlainTextRW
        for suffixs, tRW in fileTypes.items():
            if os.path.splitext(os.path.basename(fileTarget))[1] in suffixs:
                RW = tRW

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

    def set(self, key, value):
        self.fileRW.setByStringKey(key, value)

    def get(self, key):
        return self.fileRW.getByStringKey(key)

    def ls(self, page):
        r = self.fileRW.toStringTree()
        if page < 1:
            raise ValueError("无效页数")

        itemPerPage = 10
        start = (page - 1) * itemPerPage
        end = start + itemPerPage

        return r.split('\n')[start:end]

    def rm(self, key):
        self.fileRW.deleteByStringKey(key)

    def mv(self, source, dest):
        self.fileRW.renameKey(source, dest)

    def cp(self, source, dest):
        self.fileRW.copyKey(source, dest)
