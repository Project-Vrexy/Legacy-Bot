import nextcord as discord
from nextcord.ext import commands
import dislash as slash

from cogs.utils.path import path
p = path()


class SlashTest(commands.Cog):
    def __init__(self, client):
        self.client = client

    @slash.command(description="welcome to th", test_guilds=713675042143076352)
    async def bru(self, inter):
        await inter.respond("hel")

def setup(client):
    client.add_cog(SlashTest(client))