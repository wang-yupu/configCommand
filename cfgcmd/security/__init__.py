from ..shared import config

from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
import os.path
import os
from enum import Enum

from datetime import datetime
import time


class PermissionResult(Enum):
    PASS = 0
    NotAllowConfigThisPlugin = 1
    NotAllowOutBound = 2


def verifyFilePermission(targetFile, opPlayerName):
    psi: PluginServerInterface = PluginServerInterface.psi()
    if opPlayerName == "<CONSOLE>" or opPlayerName == config.cfg.get('ownerPlayer', None):
        return PermissionResult.PASS  # 永远有权限

    MCDRRootPath = os.path.abspath(os.path.dirname(os.path.dirname(psi.get_data_folder())))
    file: str = os.path.abspath(targetFile)
    # 检查是否是本插件的配置

    if not config.cfg['allowModifyConfig']:
        if file.endswith("cfgcmd.yaml"):
            return PermissionResult.NotAllowConfigThisPlugin

    # 检查是否离开了MCDR目录
    if not config.cfg['allowOutBound']:
        if os.path.commonpath([file, MCDRRootPath]) != MCDRRootPath:
            return PermissionResult.NotAllowOutBound

    return PermissionResult.PASS


def log(message):
    if config.cfg.get('enableLog', False):
        config.logsInThisSession.append(message)


def saveLogs():
    if config.cfg.get('enableLog', False):
        # 文件夹是否存在
        if not os.path.exists("./logs/cfgcmdLogs/"):
            os.mkdir("./logs/cfgcmdLogs")
        # 先获取目前的时间
        tString = datetime.now().strftime('%Y-%m-%d_')

        # 然后获取次数
        files = os.listdir("./logs/cfgcmdLogs/")
        thisCount = 0
        for item in files:
            if item.startswith(tString) and item.endswith(".log"):
                # 读取里面的次数
                try:
                    thisCount = int(item.lstrip(tString).rstrip(".log"))
                except ValueError:
                    thisCount = str(int(time.time()))[2:]

        # 文件名
        fileName = f"{tString}_{thisCount+1}.log"
        with open(os.path.join("./logs/cfgcmdLogs/", fileName), "w") as file:
            for item in config.logsInThisSession:
                file.write(item+"\n")

        # done
