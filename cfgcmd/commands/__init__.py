#
from mcdreforged.plugin.si.plugin_server_interface import PluginServerInterface

from ..shared import config
from ..fileHandler import HandlerEnum

from .basicEnvCommands import *
from .fileCommands import *

from mcdreforged.command.builder.nodes.basic import Literal
from mcdreforged.command.builder.nodes.arguments import Text, QuotableText, Enumeration, GreedyText


def registerAllCommands(serverInstance: PluginServerInterface):
    serverInstance.register_help_message("!!cfg ...", "具体查阅文档", config.cfg.get("cfgCmdPermission", 4))

    tree = Literal('!!cfg')\
        .runs(printHelp)\
        .then(Literal('env')
              .then(QuotableText("dir")
                    .then(QuotableText("file").runs(loadEnv)
                          .then(Enumeration("rwMode", HandlerEnum)
                                .runs(loadEnv)
                                )))

              )\
        .then(Literal("quit").runs(quitEnv))\
        .then(Literal("write").runs(writeFile))\
        .then(Literal("reload").runs(reloadFile))\
        .then(Literal("info").runs(infoFile))\
        .then(Literal("set").then(QuotableText("key").runs(setKV).then(GreedyText("value").runs(setKV))))\
        .then(Literal("rm").then(GreedyText('key')))\
        .then(Literal("mv").then(QuotableText('key')).then(QuotableText('key')))\
        .then(Literal("cp").then(QuotableText('key')).then(QuotableText('key')))\
        .then(Literal("cd").then(GreedyText('key')))\
        .then(Literal("ls").then(GreedyText('key')))

    tree.print_tree(serverInstance.logger.info)

    serverInstance.register_command(tree)
