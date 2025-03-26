#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface
import os
import yaml

defaultConfig = {
    "ownerPlayer": None,  # WIP
    "cfgCmdPermission": 4
}


def loadConfig(serverInstance: PluginServerInterface):
    try:
        with open(os.path.join(serverInstance.get_data_folder(), 'cfgcmd.yaml'), 'r') as fileHandler:
            cfg = yaml.safe_load(fileHandler)
    except FileNotFoundError:
        serverInstance.logger.warning("找不到配置文件，创建默认配置文件...")
        cfg = defaultConfig
        with open(os.path.join(serverInstance.get_data_folder(), 'cfgcmd.yaml'), 'w') as fileHandler:
            cfg = yaml.safe_dump(defaultConfig, fileHandler)

    return cfg
