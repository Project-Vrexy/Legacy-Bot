# Discord
from nextcord.ext import commands

# Local Code
from cogs.utils.reddit import RedditUtils


class Nsfw(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.reddit_utils = RedditUtils(client=client)
 
        self.emoji = '🔞'
        self.desc = 'Commands that can help you chug the perfect 31'

        # Extra Checks
        self.extras = {
            'hentai': {
                'is_nsfw': True,
                'guild_only': True
            },
            'rule34': {
                'is_nsfw': True,
                'guild_only': True
            },
            'yuri': {
                'is_nsfw': True,
                'guild_only': True
            },
            'yaoi': {
                'is_nsfw': True,
                'guild_only': True
            },
        }

    # Hentai
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.command(brief="Show some hentai")
    async def hentai(self, ctx):
        options = ["hentai", "animerule34"]

        await self.reddit_utils.nsfw(ctx, options)

    # Rule34
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.command(brief="Show some rule 34.")
    async def rule34(self, ctx):
        options = ["rule34", "animerule34"]

        await self.reddit_utils.nsfw(ctx, options)

    # Yuri
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.command(brief="Show some yuri.")
    async def yuri(self, ctx):
        options = ["yuri", "yurihentai"]

        await self.reddit_utils.nsfw(ctx, options)

    # Yaoi
    @commands.is_nsfw()
    @commands.guild_only()
    @commands.command(brief="Show some yaoi.")
    async def yaoi(self, ctx):
        options = ["yaoi", "catboys", "boyslove", "delicioustraps"]

        await self.reddit_utils.nsfw(ctx, options)


def setup(client):
    client.add_cog(Nsfw(client))
