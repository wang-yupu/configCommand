#
from mcdreforged.command.command_source import CommandSource
from mcdreforged.command.builder.common import CommandContext

from .utils import *

from ..fileHandler import HandlerEnum, json, yaml, toml, plain
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

    obj = getPlayerObject(source)
    if obj:
        source.reply(red(f"请先关闭已打开的文件: {obj.file}"))
        return

    dir = ctx.get("dir", None)
    file = ctx.get("file", None)
    rwMode = ctx.get("rwMode", HandlerEnum.AUTO)
    if not (dir and file):
        source.reply(red("给出目录与文件！"))
        return

    sRW = None
    if rwMode != HandlerEnum.AUTO:
        sRW = {HandlerEnum.JSON: json.JSONRW,
               HandlerEnum.YAML: yaml.YAMLRW,
               HandlerEnum.TOML: toml.TOMLRW,
               HandlerEnum.PLAIN: plain.PlainTextRW}[rwMode]

    # 拼接路径
    basicDir = source.get_server().psi().get_plugin_file_path('cfgcmd')
    basicDir = os.path.dirname(os.path.dirname(basicDir))
    file = os.path.abspath(os.path.join(basicDir, dir, file))

    failed = True
    try:
        players[getStorageName(source)] = Player(getStorageName(source), file, source.get_server().logger, sRW)
    except FileNotFoundError as error:
        source.reply(red("文件不存在"))
    except UnicodeDecodeError as error:
        source.reply(red("无法以UTF-8解码文件"))
    except PermissionError as error:
        source.reply(red("无权限"))
    except OSError as error:
        source.reply(red("系统错误，可能是文件被占用了"))
    except ValueError:
        source.reply(red("无法解析配置文件"))
    # except Exception as error:
    #     source.reply(red(f"未捕获的错误: {error}"))
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
    if obj and obj.fileChangedAndQuitWithoutSave and obj.fileChangedAndNotSave:
        source.reply(orange("成功不保存并关闭了文件"))
        return
    elif obj and obj.fileChangedAndNotSave:
        source.reply(orange("文件还有未保存的修改，再次输入此命令以不保存并关闭"))
        obj.fileChangedAndQuitWithoutSave = True
    else:
        source.reply(green("成功关闭了文件"))
        del players[getStorageName(source)]


def writeFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    obj = players.get(getStorageName(source), None)
    obj.write()
    source.reply(green("成功写入文件"))


def infoFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    obj = players.get(getStorageName(source), None)
    if not obj:
        source.reply(red("还没有打开文件"))
        return

    t = orange("--- 文件信息 ---") + endl() + white("文件: ") + aqua(obj.file) + \
        endl() + white("使用的读写器: ") + aqua(obj.fileRW.typ)
    source.reply(t)

    if not obj.fileChangedAndNotSave:
        return

    t2 = orange("--- 暂存的修改 ---") + endl()
    i = 0
    for op in obj.operations:
        t2 += gray(f"{i}. ") + white(op) + endl()
        i += 1

    source.reply(t2)


def reloadFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return
    obj = players.get(getStorageName(source), None)
    obj.load()
    source.reply(green("成功地重载了文件"))
