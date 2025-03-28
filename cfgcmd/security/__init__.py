from ..shared import config

from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
import os.path
from enum import Enum


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
