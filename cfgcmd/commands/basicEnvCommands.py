#
from mcdreforged.command.command_source import CommandSource
from mcdreforged.command.builder.common import CommandContext

from .utils import *

from ..fileHandler import HandlerEnum
from ..playerEnv import Player
from ..shared.playerEnv import players

import os.path


def printHelp(source: CommandSource, ctx: CommandContext):
    source.reply(aqua(f"configCommand v{source.get_server().get_plugin_metadata('cfgcmd').version}"))
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此插件！"))
        return
    source.reply(epic("< --- cfgcmd 可用命令 --- >"))
    source.reply(orange("基本: ")+white("env quit write reload info"))
    source.reply(orange("键值对操作: ")+white("set rm mv cp cd ls"))


def loadEnv(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    dir = ctx.get("dir", None)
    file = ctx.get("file", None)
    rwMode = ctx.get("rwMode", HandlerEnum.AUTO)
    source.reply(white(f"{dir} {file} {rwMode}"))
    if not (dir and file):
        source.reply(red("给出目录与文件！"))
        return

    # 拼接路径
    basicDir = source.get_server().psi().get_plugin_file_path('cfgcmd')
    basicDir = os.path.dirname(os.path.dirname(basicDir))
    file = os.path.abspath(os.path.join(basicDir, dir, file))

    failed = True
    try:
        players[getStorageName(source)] = Player(getStorageName(source), file, source.get_server().logger)
    except FileNotFoundError as error:
        source.reply(red("文件不存在"))
    except UnicodeDecodeError as error:
        source.reply(red("无法以UTF-8解码文件"))
    except PermissionError as error:
        source.reply(red("无权限"))
    except OSError as error:
        source.reply(red("系统错误，可能是文件被占用了"))
    except Exception as error:
        source.reply(red(f"未捕获的错误: {error}"))
    else:
        failed = False
    if failed:
        source.reply(gray(f"无法打开文件: {file}"))
        return

    source.reply(green(f"打开了配置文件: {file}，你现在可以对它进行操作了。记得使用`!!cfg write`保存"))


def quitEnv(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    if not players.get(getStorageName(source), None):
        source.reply(red("没有打开的文件"))
        return

    obj = players.get(getStorageName(source), None)
    if obj and obj.fileChangedAndQuitWithoutSave:
        source.reply(orange("成功不保存并关闭了文件"))
        return
    elif obj and obj.fileChangedAndNotSave:
        source.reply(orange("文件还有未保存的修改，再次输入此命令以不保存并关闭"))
    else:
        source.reply(green("成功关闭了文件"))


def writeFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    obj = players.get(getStorageName(source), None)
    obj.fileChangedAndNotSave = False


def infoFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    source.reply(orange("...info"))


def reloadFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    source.reply(orange("...reload"))
