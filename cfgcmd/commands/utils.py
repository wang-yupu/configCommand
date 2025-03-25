#
from mcdreforged.minecraft.rtext.text import RText
from mcdreforged.minecraft.rtext.style import RColor
from mcdreforged.command.command_source import CommandSource
from ..shared.config import cfg


def verifyPermission(source: CommandSource):
    if source.get_permission_level() < cfg.get("cfgCmdPermission", 4):
        return False
    return True


def getStorageName(source: CommandSource):
    if source.is_console:
        return "<CONSOLE>"
    elif source.is_player:
        return source.player
    else:
        return "<UNKNOWN>"


def red(text: str) -> RText:
    return RText(text, RColor.red)


def green(text: str) -> RText:
    return RText(text, RColor.green)


def aqua(text: str) -> RText:
    return RText(text, RColor.aqua)


def blue(text: str) -> RText:
    return RText(text, RColor.blue)


def orange(text: str) -> RText:
    return RText(text, RColor.gold)


def gray(text: str) -> RText:
    return RText(text, RColor.gray)


def white(text: str) -> RText:
    return RText(text, RColor.white)


def epic(text: str) -> RText:
    return RText(text, RColor.dark_purple)
