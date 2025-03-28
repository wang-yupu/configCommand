#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface

from .config import loadConfig

from .shared import config

from .commands import registerAllCommands


def on_load(server: PluginServerInterface, _):
    server.logger.info(f"configCommand v{server.get_plugin_metadata('cfgcmd').version} 开始加载")

    config.cfg = loadConfig(server)
    server.logger.info(config.cfg)

    registerAllCommands(server)
