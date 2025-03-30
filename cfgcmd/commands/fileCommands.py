#
from mcdreforged.command.command_source import CommandSource
from mcdreforged.command.builder.common import CommandContext

from .utils import *
from ..playerEnv import TypeNotValidError
from ..security import log

import os.path


from datetime import datetime


def getTimeString():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def setKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    player = getPlayerObject(source)

    try:
        old = player.get(ctx.get("key"))
    except:
        old = "无"

    try:
        player.set(ctx.get("key"), ctx.get("value"))
    except KeyError:
        source.reply(red("不存在的键"))
    except Exception as error:
        source.reply(red(f"无法修改，错误: {error}"))
    source.reply(green(f"将 {ctx.get("key")} 由 {old} 修改为 {ctx.get("value")}"))


def setKVTyped(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    player = getPlayerObject(source)

    try:
        old = player.get(ctx.get("key"))
    except:
        old = "无"

    try:
        player.set(ctx.get("key"), ctx.get("value"), ctx.get('type'))
    except KeyError:
        source.reply(red("不存在的键"))
    except TypeNotValidError:
        source.reply(red(f"无法将类型 {ctx.get('type')} 应用于值上"))
    except Exception as error:
        source.reply(red(f"无法修改，错误: {error}"))
    source.reply(green(f"将 {ctx.get("key")} 由 {old} 修改为 {ctx.get("value")}，指定了类型: {ctx.get('type').name}"))


def rmKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    try:
        obj = getPlayerObject(source)
        obj.rm(ctx.get("key"))
        source.reply(green(f"删除了 {ctx.get("key")}"))
    except KeyError:
        source.reply(red("不存在的键"))


def mvKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    try:
        obj = getPlayerObject(source)
        obj.mv(ctx.get('key1'), ctx.get('key2'))

        source.reply(green(f"移动 {ctx.get('key1')} 到 {ctx.get('key2')}"))
    except KeyError:
        source.reply(red("不存在的原键"))


def cpKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    try:
        obj = getPlayerObject(source)
        obj.cp(ctx.get('key1'), ctx.get('key2'))

        source.reply(green(f"移动 {ctx.get('key1')} 到 {ctx.get('key2')}"))
    except KeyError:
        source.reply(red("不存在的原键"))


def cdKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    obj = getPlayerObject(source)
    obj.currentCursor = ctx.get('key')
    source.reply(green(f"切换到: {ctx.get('key')}"))


def lsKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    if not getObjectExists(source):
        source.reply(red("文件未加载"))
        return

    player = getPlayerObject(source)
    page = ctx.get('page', None)
    linePerPage = ctx.get('linePerPage', 10)
    if not page:
        page = 1
    elif page < 1:
        source.reply(red("无效页数"))
        return

    elif page > player.getPageCount(linePerPage):
        source.reply(red(f"页数过大, 此文件只有 {player.getPageCount()} 页"))
        return

    source.reply(epic(f"--- 查看 第{page}页 ---"))
    for line in player.ls(page, linePerPage):
        source.reply(line)
    source.reply(epic(f'----- {page} / {player.getPageCount()} -----'))


def rmFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    file = ctx.get("file")
    if not os.path.exists(file):
        source.reply(red("文件不存在"))
        return
    try:
        os.remove(file)
        source.reply(green("成功移除了目标文件(无法后悔)"))
    except:
        source.reply(red("无法删除目标文件"))
        log(f"[File] [{getStorageName(source)}] [{getTimeString()}] Removed: {file}")


def touchFile(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    try:
        file = ctx.get("file")
        if os.path.exists(file):
            source.reply(red("文件已存在"))
            return
        with open(file, 'w') as _:
            pass
    except:
        source.reply(red("无法创建新的空文件"))
    else:
        source.reply(green("成功创建了新的空文件"))
        log(f"[File] [{getStorageName(source)}] [{getTimeString()}] Created new empty file: {file}")


def lsDir(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此命令！"))
        return

    dir = ctx.get("path", ".")

    basicDir = source.get_server().psi().get_plugin_file_path('cfgcmd')
    basicDir = os.path.dirname(os.path.dirname(basicDir))
    tPath = os.path.abspath(os.path.join(basicDir, dir))

    try:
        lst = os.listdir(tPath)
        t = orange(f"lsDir: {tPath}") + endl()
        for item in lst:
            t += white(item) + endl()
        log(f"[ReadOnly] [{getStorageName(source)}] [{getTimeString()}] List dir: {tPath}")
        source.reply(t)
    except:
        source.reply(red("出错"))
