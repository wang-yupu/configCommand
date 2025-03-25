#
from mcdreforged.command.command_source import CommandSource
from mcdreforged.command.builder.common import CommandContext

from .utils import *


def setKV(source: CommandSource, ctx: CommandContext):
    source.reply(green(f"K: {ctx.get('key')}, V: {ctx.get('value')}"))


def rmKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此插件！"))


def mvKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此插件！"))


def cpKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此插件！"))


def cdKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此插件！"))


def lsKV(source: CommandSource, ctx: CommandContext):
    if not verifyPermission(source):
        source.reply(red("你没有足够的权限以使用此插件！"))
