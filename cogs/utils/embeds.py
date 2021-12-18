# Discord
import nextcord as discord


class EmbedUtils:
    def __init__(self, client):
        self.client = client
    
    @staticmethod
    async def field_title(embed, title):
        embed.add_field(name="\u200b", value=f"**{title}**", inline=False)

    @staticmethod
    async def spacer(embed):
        embed.add_field(name='\u200b', value='\u200b', inline=False)


class NoticeEmbeds:
    def __init__(self, client):
        self.client = client

    @staticmethod
    async def load(ctx, message):
        return await ctx.reply(
            embed=discord.Embed(
                title=f"<a:load:827975573443051570> {message}...",
                color=discord.Color.green()
            ),
            mention_author=False
        )

    @staticmethod
    async def error(context, title, description):
        e = discord.Embed(
            title=f":x: {title}",
            color=discord.Color.red(),
            description=description
        )

        # e.set_thumbnail(url=self.client.user.display_avatar.url)
        await context.reply(embed=e, mention_author=False)

    @staticmethod
    async def load_error(load, title, description):
        e = discord.Embed(
            title=f":x: {title}",
            color=discord.Color.red(),
            description=description
        )

        await load.edit(embed=e)

    @staticmethod
    async def no_perms(context, title, description):
        e = discord.Embed(
            title=f":no_entry: {title}",
            color=discord.Color.red(),
            description=description
        )

        # e.set_thumbnail(url=self.client.user.display_avatar.url)
        await context.reply(embed=e, mention_author=False)
    
    @staticmethod
    async def perform_action(ctx, cmd, cmds):
        e = discord.Embed(
            title=":thinking: What action are you trying to perform?",
            color=discord.Color.green(),
            description=f"If you don't know what to do, try using `{ctx.prefix}{cmd} help` to see available {cmds} "
                        f"commands."
        )

        # e.set_thumbnail(url=self.client.user.display_avatar.url)
        await ctx.reply(mention_author=False, embed=e)
