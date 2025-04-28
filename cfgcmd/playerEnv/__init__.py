#
from logging import Logger
from ..fileHandler import json, yaml, toml, plain, TypeEnum
import math
import re
from ..security import verifyFilePermission, PermissionResult, log
from datetime import datetime
from enum import Enum
import os
from ..cloud import CloudSession, applyResult
from mcdreforged.api.decorator import new_thread
from mcdreforged.api.rtext import RText, RColor
import time
from threading import Lock
from copy import deepcopy
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface


class TypeNotValidError(Exception):
    ...


class NoPermissionError(Exception):
    ...


def getTimeString():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


class StartSessionResult(Enum):
    unsavedChanges = 0
    alreadyOpenSession = 1
    done = 2
    failed = 3
    tooLarge = 4
    unsupportedHighlight = 5
    cloudNotAllow = 6
    cloudUnavailable = 7


class Player:
    fileChangedAndNotSave = False
    fileChangedAndQuitWithoutSave = False

    def __init__(self, playerName: str, fileTarget: str, logger: Logger, specificRW=None):
        self.psi = PluginServerInterface.psi()
        # 读取
        self.logger = logger
        logger.info(f"尝试读取文件: {fileTarget}")
        self.file = fileTarget
        self.lock = Lock()

        self.fileContent = None
        self.playerName = playerName
        self.operations = []
        self.cloudSession = None

        self.currentCursor = '.'

        self.load(syncRW=False)

        # 判断文件类型
        if specificRW:
            self.RW = specificRW
        else:
            fileTypes = {
                ('json',): json.JSONRW,
                ('yaml', 'yml'): yaml.YAMLRW,
                ('toml',): toml.TOMLRW
            }

            self.RW = plain.PlainTextRW
            for suffixs, tRW in fileTypes.items():
                for suffix in suffixs:
                    if fileTarget.endswith(suffix):
                        self.RW = tRW

        # 实例化rw
        try:
            self.fileRW = self.RW()
            self.fileRW.load(self.fileContent)
        except:
            try:
                logger.warning("回落到纯文本...")
                self.RW = plain.PlainTextRW
                self.fileRW = self.RW()
                self.fileRW.load(self.fileContent)
            except:
                raise ValueError("纯文本解析失败，也许是插件的问题")

    def write(self, content=None):
        try:
            with open(self.file, mode='w', encoding='utf-8') as file:
                file.write(content if content else self.fileRW.dump())
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
            log(f"[SAVE!] [{self.playerName}] [{getTimeString}]: Save changes of {self.file}")
            self.operations.clear()

    def load(self, writeToValue=True, syncRW=True):
        pmrs = verifyFilePermission(self.file, self.playerName, self.psi)
        if pmrs != PermissionResult.PASS:
            log(f"[ReadOnly] [{self.playerName}] [{getTimeString}]: Reading {self.file} but no permission")
            match pmrs:
                case PermissionResult.NotAllowConfigThisPlugin:
                    raise NoPermissionError("你不能修改此插件的配置文件")
                case PermissionResult.NotAllowOutBound:
                    raise NoPermissionError("你没有权限访问MCDR路径外的文件")
                case PermissionResult.NotInAllowList:
                    raise NoPermissionError("此文件不允许被修改")

        try:
            with open(self.file, 'r', encoding='utf-8') as file:
                content = file.read()
                if writeToValue:
                    self.fileContent = deepcopy(content)
                    if syncRW:
                        self.fileRW.load(self.fileContent)
            log(f"[ReadOnly] [{self.playerName}] [{getTimeString}]: Readed {self.file}")
            return content
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

    # region 在线编辑器

    def startSession(self, replyFunction) -> StartSessionResult:
        if self.lock.acquire(False):
            if self.fileChangedAndNotSave:
                return StartSessionResult.unsavedChanges
            if self.cloudSession:
                return StartSessionResult.alreadyOpenSession

            # 大小
            # 大小在服务端目前限制10MB（包含HTTP头与POST BODY）
            if os.path.getsize(self.file) > 10 * 1024 * 1024 * 0.8:
                return StartSessionResult.tooLarge

            replyFunction(RText("正在准备编辑器会话", RColor.aqua))
            self.startSessionInternal(replyFunction)
        else:
            replyFunction(RText("编辑器交互锁被占用，请稍等", RColor.red))

    @new_thread
    def startSessionInternal(self, replyFunction):
        content = self.load(False)

        self.cloudSession = CloudSession(os.path.basename(self.file), content, self.playerName,
                                         os.path.basename(os.path.dirname(self.file)), self.psi.get_plugin_metadata('cfgcmd').version)

        while not self.cloudSession.checkReady():
            time.sleep(1)

        url = self.cloudSession.getEditorURL()
        urlRText = RText.from_json_object({"text": url, "color": 'blue', "underlined": True,
                                           "clickEvent": {"action": "open_url", "value": url}})
        replyFunction(RText("编辑器链接: ", RColor.green)+urlRText+RText("(点击以打开)", RColor.gray))
        self.lock.release()

    @new_thread
    def applyChanges(self, replyFunction):
        from ..commands.utils import red
        if self.lock.acquire(False):
            if self.cloudSession:
                if self.cloudSession.checkReady():
                    replyFunction(RText("正在从服务器获取新内容", RColor.green))
                    content, status = self.cloudSession.applyChanges()
                    if status == applyResult.SUCCESS:
                        # 写入文件
                        try:
                            self.write(content)
                        except Exception as error:
                            replyFunction(red("错误: "+error))
                            self.lock.release()
                            return
                        self.load()
                        replyFunction(RText("成功更新内容", RColor.green))
                    else:
                        match status:
                            case applyResult.EXPIRE:
                                replyFunction(red("会话已过期"))
                            case applyResult.RATELIMIT:
                                replyFunction(red("遇到了限速，请稍后再试: 500 RPD , 80 RPH"))
                            case applyResult.UNREADY:
                                replyFunction(red("会话还未就绪"))
                            case applyResult.NETWORK:
                                replyFunction(red("网络问题导致无法连接至服务器"))
                    self.lock.release()
                else:
                    replyFunction(red("会话未就绪"))
                    self.lock.release()
            else:
                replyFunction(red("会话不存在"))
                self.lock.release()
        else:
            replyFunction(RText("编辑器交互锁被占用，请稍等", RColor.red))

    def deleteSession(self, replyFunction):
        from ..commands.utils import red, green
        if self.lock.acquire(False):
            if self.cloudSession:
                if self.cloudSession.checkReady():
                    self.cloudSession.deleteSession()
                    self.cloudSession = None
                    replyFunction(green("成功移除了当前编辑会话"))
                else:
                    replyFunction(red("会话未就绪"))
            else:
                replyFunction(red("会话不存在"))
            self.lock.release()
        else:
            replyFunction(RText("编辑器交互锁被占用，请稍等", RColor.red))

    # endregion
    # region 文件操作命令实现

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

                    factoryFunction = int
                    if value.count(".") != 0:
                        factoryFunction = float
                    if value.startswith('.') or value.endswith('.'):
                        return str(value)

                    return -factoryFunction(value) if intIsNegative else factoryFunction(value)
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
        ext = None
        if isinstance(value, float):
            ext = "浮点数"
        self.fileRW.setByStringKey(key, value)
        self.fileChangedAndNotSave = True
        self.operations.append(f"set {key}: {value}")
        log(f"[Unsaved] [{self.playerName}] [{getTimeString}]: SET K:<{key}> to V:<{value}> ")
        return ext, value

    def get(self, key):
        key = self.postProcessKey(key)
        return self.fileRW.getByStringKey(key)

    def ls(self, page, itemPerPage=10):
        r = self.fileRW.toStringTree()
        if page < 1:
            raise ValueError("无效页数")

        start = (page - 1) * itemPerPage
        end = start + itemPerPage
        log(f"[ReadOnly] [{self.playerName}] [{getTimeString}]: Read current file at page {page}")

        return r[start:end]

    def getPageCount(self, itemPerPage=10) -> int:
        return math.ceil(len(self.fileRW.toStringTree())/itemPerPage)

    def rm(self, key):
        key = self.postProcessKey(key)
        self.fileRW.deleteByStringKey(key)
        self.fileChangedAndNotSave = True
        self.operations.append(f"rm {key}")
        log(f"[Unsaved] [{self.playerName}] [{getTimeString}]: Remove key: {key}")

    def mv(self, source, dest):
        source = self.postProcessKey(source)
        dest = self.postProcessKey(dest)
        self.fileRW.renameKey(source, dest)
        self.fileChangedAndNotSave = True
        self.operations.append(f"mv {source} to {dest}")
        log(f"[Unsaved] [{self.playerName}] [{getTimeString}]: Move {source} to {dest}")

    def cp(self, source, dest):
        source = self.postProcessKey(source)
        dest = self.postProcessKey(dest)
        self.fileRW.copyKey(source, dest)
        self.fileChangedAndNotSave = True
        self.operations.append(f"cp {source} to {dest}")
        log(f"[Unsaved] [{self.playerName}] [{getTimeString}]: Copy {source} to {dest}")

    # endregion
