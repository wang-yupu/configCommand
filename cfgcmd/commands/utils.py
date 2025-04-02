#
from mcdreforged.minecraft.rtext.text import RText
from mcdreforged.minecraft.rtext.style import RColor, RStyle
from mcdreforged.command.command_source import CommandSource
from ..shared.config import cfg
from ..shared.playerEnv import players


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


def getPlayerObject(source: CommandSource):
    return players.get(getStorageName(source), None)


def getObjectExists(source: CommandSource) -> bool:
    return players.get(getStorageName(source), False)


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


def darkred(text: str) -> RText:
    return RText(text, RColor.dark_red)


def endl() -> RText:
    return RText("\n")


def bold(text: str | RText, color: RColor = None):
    if color:
        return RText(text).set_styles({RStyle.bold, color})
    else:
        return RText(text, RStyle.bold)


def italic(text: str | RText, color: RColor = None):
    if color:
        return RText(text).set_styles({RStyle.italic, color})
    else:
        return RText(text, RStyle.italic)
