#
from logging import Logger
from ..fileHandler import json, yaml, toml, plain, TypeEnum
import math
import re


class TypeNotValidError(Exception):
    ...


class Player:
    fileChangedAndNotSave = False
    fileChangedAndQuitWithoutSave = False

    def __init__(self, playerName: str, fileTarget: str, logger: Logger, specificRW=None):
        # 读取
        logger.info(f"尝试读取文件: {fileTarget}")
        self.file = fileTarget

        self.fileContent = None
        self.playerName = playerName
        self.operations = []

        self.currentCursor = '.'

        self.load()

        # 判断文件类型
        if specificRW:
            RW = specificRW
        else:
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

    def isTypeAvailableForValue(self, value: str, type: TypeEnum) -> bool:
        if type == TypeEnum.AUTO:
            return ValueError("适合的类型不能为AUTO")
        elif type == TypeEnum.STRING:
            return True
        elif type == TypeEnum.INT:
            # 判断可能的小数点和负号
            if not set(value).issubset({"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "-"}):
                return False
            # 负号处理
            if value.count("-") > 1:
                return False  # 出现了多个负号
            elif value.startswith("-"):
                value = value.lstrip("-")

            # 小数点
            if value.count(".") > 1:
                # 2+个小数点
                lastDotPos = value.rfind(".")
                value = value[:lastDotPos].replace(".", "") + value[lastDotPos:]
            if value.startswith('.') or value.endswith('.'):
                return False

            return True
        elif type == TypeEnum.BOOL:
            if value.upper() in ['TRUE', 'FALSE', 'T', 'F']:
                return True
        elif type == TypeEnum.LIST:
            # 返回常量
            return True
        elif type == TypeEnum.OBJECT:
            KVs = re.split(r'(?!\\),', value)
            # 检查每个键值对
            for KV in KVs:
                splitedKV = re.split(r'(?!\\):', KV)
                if len(splitedKV) != 2:
                    return False
            return True
        elif type == TypeEnum.NONE:
            return True

    def pyTypeToEnum(self, value: any) -> TypeEnum:
        if isinstance(value, str):
            return TypeEnum.STRING
        elif isinstance(value, int) or isinstance(value, float):
            return TypeEnum.INT
        elif isinstance(value, bool):
            return TypeEnum.BOOL
        elif isinstance(value, list) or isinstance(value, set):
            return TypeEnum.LIST
        elif isinstance(value, dict):
            return TypeEnum.OBJECT
        elif value == None:
            return TypeEnum.NONE

    def convertValue(self, value: str, type: TypeEnum):
        match type:
            case TypeEnum.STRING:
                return str(value)
            case TypeEnum.INT:
                if self.isTypeAvailableForValue(value, type):
                    # 处理数字
                    intIsNegative = False
                    if value.startswith('-'):
                        intIsNegative = True
                        value.lstrip("-")

                    # 小数点
                    if value.count(".") > 1:
                        # 2+个小数点
                        lastDotPos = value.rfind(".")
                        value = value[:lastDotPos].replace(".", "") + value[lastDotPos:]
                    if value.startswith('.') or value.endswith('.'):
                        return str(value)

                    return -int(value) if intIsNegative else int(value)
                else:
                    return str(value)
            case TypeEnum.BOOL:
                if value.upper() in ['TRUE', 'FALSE', 'T', 'F'] and self.isTypeAvailableForValue(value, type):
                    if value.upper().startswith("T"):
                        return True
                    elif value.upper().startswith("F"):
                        return False
                return str(value)
            case TypeEnum.LIST:
                if self.isTypeAvailableForValue(value, type):
                    return re.split(r'(?!\\),', value)
                return str(value)
            case TypeEnum.OBJECT:
                if self.isTypeAvailableForValue(value, type):
                    KVs = re.split(r'(?!\\),', value)
                    result = {}
                    for item in KVs:
                        k, v = re.split(r'(?!\\):', item)
                        result[k] = v
                    return result
            case TypeEnum.NONE:
                return None

        return str(value)

    def autoType(self, value: str, rValue: any, typed: TypeEnum):
        print(rValue)
        if typed != TypeEnum.AUTO and typed != None:  # 指定类型
            if self.isTypeAvailableForValue(value, typed):
                return self.convertValue(value, typed)
            else:
                raise TypeNotValidError("无法转换为目标类型")

        # 开始类型推导
        # 1. 原先值是否不存在或值为None?
        if rValue:  # 原值存在
            rValueType = self.pyTypeToEnum(rValue)
            if self.isTypeAvailableForValue(value, rValueType):
                # 类型转换，使用原类型
                return self.convertValue(value, rValueType)
        if value == 'None':
            return None

        # 2. 是否是布尔值?
        if value.upper() in ["T", "TRUE", 'F', "FALSE"]:
            return self.convertValue(value, TypeEnum.BOOL)

        # 3. 包含非数字字符(小数点、负号除外)?
        if not set(value).issubset({"1", "2", "3", "4", "5", "6", "7", "8", "9", "0", ".", "-", '"'}):
            return str(value)  # 结束

        # 4. 不完全是字符串
        if value.count('"') == 2 and value.startswith('"') and value.endswith('"'):
            return str(self.convertValue(value.strip('"'), TypeEnum.INT))

        # 5. 那就是数字了
        if self.isTypeAvailableForValue(value, TypeEnum.INT):
            return self.convertValue(value, TypeEnum.INT)

        # 6. ?
        return str(value)

    def set(self, key, value: str, typed: TypeEnum = None):
        key = self.postProcessKey(key)
        # 处理数据类型
        try:
            rValue = self.get(key)
        except KeyError:
            rValue = None
        value = self.autoType(value, rValue, typed)
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
