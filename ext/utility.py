from __future__ import annotations
import random
import re
import string
from datetime import timedelta
from typing import Any, Callable, Optional, Tuple, Union, TYPE_CHECKING

import discord
from discord.ext import commands
from discord.ext.commands import check

from ext.time import UserFriendlyTime

if TYPE_CHECKING:
    from bot import rainbot
    from ext.database import DBDict
    from ext.command import RainCommand, RainGroup  # noqa: F401


with open('ext/emojis.txt', encoding='utf8') as f:
    UNICODE_EMOJI = '|'.join(map(re.escape, f.read().splitlines()))
UNICODE_EMOJI_REGEX = re.compile(UNICODE_EMOJI)
# File is parsed from js files from loading up discord


__all__ = ('get_perm_level', 'format_timedelta')


def get_perm_level(member: discord.Member, guild_config: 'DBDict') -> Tuple[int, Union[str, discord.Role, None]]:
    # User is not in server
    highest_role: Union[str, discord.Role, None] = None

    if not getattr(member, 'guild_permissions', None):
        perm_level = 0
        highest_role = None
    elif member.id == member.guild.me.id:
        # if its the bot
        perm_level = 100
        highest_role = 'Bot'
    elif member.guild_permissions.administrator:
        perm_level = 15
        highest_role = 'Administrator'
    elif member.guild_permissions.manage_guild:
        perm_level = 10
        highest_role = 'Manage Server'
    else:
        perm_level = 0
        highest_role = None

        perm_levels = [int(i.role_id) for i in guild_config.perm_levels]
        for i in reversed(member.roles):
            if i.id in perm_levels:
                new_perm_level = guild_config.perm_levels.get_kv('role_id', str(i.id)).level
                if new_perm_level > perm_level:
                    perm_level = new_perm_level
                    highest_role = i

    return (perm_level, highest_role)


def get_command_level(cmd: Union['RainCommand', 'RainGroup'], guild_config: 'DBDict') -> int:
    name = cmd.qualified_name

    try:
        perm_level = guild_config.command_levels.get_kv('command', name).level
    except IndexError:
        perm_level = cmd.perm_level

    return perm_level


def lower(argument: str) -> str:
    return str(argument).lower()


def owner() -> Callable:
    def predicate(ctx: commands.Context) -> bool:
        return ctx.author.id in ctx.bot.owners
    return check(predicate)


def random_color() -> int:
    return random.randint(0, 0xfffff)


def format_timedelta(delta: Union[int, timedelta], *, assume_forever: bool=True) -> str:
    if not delta:
        if assume_forever:
            return 'forever'
        else:
            return '0 seconds'

    if isinstance(delta, timedelta):
        seconds = int(delta.total_seconds())
    else:
        seconds = int(delta)

    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    months, days = divmod(days, 30)
    years, months = divmod(months, 12)

    fmt = ''
    if seconds:
        fmt = f'{seconds} seconds ' + fmt
    if minutes:
        fmt = f'{minutes} minutes ' + fmt
    if hours:
        fmt = f'{hours} hours ' + fmt
    if days:
        fmt = f'{days} days ' + fmt
    if months:
        fmt = f'{months} months ' + fmt
    if years:
        fmt = f'{years} years ' + fmt

    return fmt.strip()


def tryint(x: str) -> Union[str, int]:
    try:
        return int(x)
    except (ValueError, TypeError):
        return x


class EmojiOrUnicode(commands.Converter):
    async def convert(self, ctx: commands.Context, argument: str) -> Union[discord.Emoji, UnicodeEmoji]:
        try:
            return await commands.EmojiConverter().convert(ctx, argument)
        except commands.BadArgument:
            if isinstance(argument, str):
                if UNICODE_EMOJI_REGEX.match(argument):
                    return UnicodeEmoji(argument)
                else:
                    raise commands.BadArgument('Invalid emoji provided')


class UnicodeEmoji:
    def __init__(self, id: str) -> None:
        self.id = id


class SafeFormat(dict):
    def __init__(self, **kw: Any) -> None:
        self.__dict = kw

    def __getitem__(self, name: str) -> Any:
        return self.__dict.get(name, SafeString('{%s}' % name))


class SafeString(str):
    def __getattr__(self, name: str) -> Optional[str]:
        try:
            return getattr(self, name)
        except AttributeError:
            return SafeString('%s.%s}' % (self[:-1], name))


def apply_vars(bot: 'rainbot', tag: str, message: discord.Message, user_input: str) -> str:
    return string.Formatter().vformat(tag, [], SafeFormat(
        invoked=message,
        guild=message.guild,
        channel=message.channel,
        bot=bot.user,
        input=user_input
    ))


class Detection:
    def __init__(self, func: Callable, *, name, check_enabled=True, require_user=None, allow_bot=False, require_prod=True, require_guild=True, require_attachment=False, force_enable=False):
        self.callback = func
        self.name = name
        self.check_enabled = check_enabled
        self.require_user = require_user
        self.allow_bot = allow_bot
        self.require_prod = require_prod
        self.require_guild = require_guild
        self.require_attachment = require_attachment
        self.force_enable = force_enable

        self.__cog_detection__ = True

    async def check_constraints(self, bot: rainbot, message: discord.Message) -> bool:
        if self.require_guild and not message.guild:
            return False

        if self.force_enable and bot.dev_mode:
            return True

        if message.guild:
            guild_config = await bot.db.get_guild_config(message.guild.id)

            if self.check_enabled and not guild_config.detections[self.name]:
                return False

            if str(message.channel.id) in guild_config.ignored_channels[self.name]:
                return False

            if not bot.dev_mode and str(message.channel.id) in guild_config.ignored_channels_in_prod:
                return False

            if get_perm_level(message.author, guild_config)[0] >= 5:
                return False

        if self.require_user and message.author.id != self.require_user:
            return False

        if not self.allow_bot and message.author.bot:
            return False

        if self.require_prod and bot.dev_mode:
            return False

        if self.require_attachment and not message.attachments:
            return False

        return True

    async def trigger(self, cog: commands.Cog, message: discord.Message) -> Any:
        if await self.check_constraints(cog.bot, message):
            message = MessageWrapper(message)
            message.detection = self
            cog.bot.loop.create_task(self.callback(cog, message))

    async def punish(self, bot: rainbot, message: discord.Message, *, reason=None, purge_limit=None):
        ctx = DummyContext(await bot.get_context(message))
        ctx.author = message.guild.me  # bot

        guild_config = await bot.db.get_guild_config(message.guild.id)
        punishments = guild_config.detection_punishments[self.name]

        reason = reason or f'Detection triggered: {self.name}'

        for _ in range(punishments.warn):
            ctx.command = bot.get_command('warn add')
            await ctx.invoke(bot.get_command('warn add'), member=message.author, reason=reason)

        if punishments.kick:
            try:
                ctx.command = bot.get_command('kick')
                await ctx.invoke(bot.get_command('kick'), member=message.author, reason=reason)
            except discord.NotFound:
                pass

        if punishments.ban:
            try:
                ctx.command = bot.get_command('ban')
                await ctx.invoke(bot.get_command('ban'), member=message.author, reason=reason)
            except discord.NotFound:
                pass

        if punishments.delete:
            if purge_limit:
                ctx.command = bot.get_command('purge')
                await ctx.invoke(bot.get_command('purge'), member=message.author, limit=purge_limit)
            else:
                try:
                    await message.delete()
                except discord.NotFound:
                    pass

        if punishments.mute:
            try:
                time = await UserFriendlyTime(default='nil').convert(ctx, punishments.mute)
            except commands.BadArgument:
                # ignore as bad argument
                pass
            else:
                delta = time.dt - message.created_at
                try:
                    await bot.mute(ctx.author, message.author, delta, reason=reason)
                except discord.NotFound:
                    pass


def detection(name: str, **attrs: bool) -> Callable:
    def decorator(func: Callable) -> Detection:
        return Detection(func, name=name, **attrs)
    return decorator


class QuickId:
    def __init__(self, guild_id: int, id_: int):
        self.guild_id = guild_id
        self.id = id_


class MessageWrapper:
    def __init__(self, message: discord.Message):
        self._message = message

    def __getattr__(self, item: str) -> Any:
        return getattr(self._message, item)


class DummyContext:
    def __init__(self, context: commands.Context):
        self._context = context
        self._dummy = True

    def __getattr__(self, item: str) -> Any:
        return getattr(self._context, item)

    async def send(self, *args: Any, **kwargs: Any) -> None:
        # block ctx.send
        pass

    async def invoke(self, *args: Any, **kwargs: Any) -> None:
        """Overwrite so invoke uses DummyContext"""

        try:
            command = args[0]
        except IndexError:
            raise TypeError('Missing command to invoke.') from None

        arguments = []
        if command.cog is not None:
            arguments.append(command.cog)

        arguments.append(self)
        arguments.extend(args[1:])

        ret = await command.callback(*arguments, **kwargs)
        return ret


class CannedStr(commands.Converter):
    def __init__(self, additional_vars={}):
        self.additional_vars = additional_vars

    async def convert(self, ctx: commands.Context, argument: str) -> str:
        guild_config = await ctx.bot.db.get_guild_config(ctx.guild.id)

        canned = self.additional_vars.copy()
        canned.update(guild_config.canned_variables)

        return string.Formatter().vformat(argument, [], SafeFormat(
            **canned
        ))
