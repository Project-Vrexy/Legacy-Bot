# Discord
from nextcord.ext import commands


# BlackList: Exception
class UserIsBlacklisted(commands.CheckFailure):
    def __str__(self):
        return "You are not allowed to use this bot"


class GuildDisabledCommand(commands.CheckFailure):
    def __str__(self):
        return "Your guild has disabled this command"


class DeafError(Exception):
    pass
