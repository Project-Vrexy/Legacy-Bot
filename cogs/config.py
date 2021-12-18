# Discord
import nextcord as discord
from nextcord.ext import commands

# Third Party
import aiosqlite
from aiosqlite import connect

# Local Code
from cogs.utils.embeds import NoticeEmbeds


class Config(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.emoji = '⚙️'
        self.desc = 'Configure Aeon\'s moderation in your server'
        self.not_everyone = True

        self.extras = {
            'antiswear': {
                'guild_only': True
            },
            'prefix': {
                'guild_only': True
            }
        }
        self.notice_embeds = NoticeEmbeds(client)

    async def cog_check(self, ctx):
        return commands.guild_only()

    @commands.group(
        brief="Configure Aeon's Anti-Swear Filter using this command", aliases=["as", "filter"]
    )
    @commands.has_permissions(manage_messages=True)
    async def antiswear(self, ctx):
        if ctx.invoked_subcommand is not None:
            return
        async with connect(self.client.db) as db:
            async with db.execute('SELECT swears, delete_swear, log_channel, wildcard FROM config where id = :id', {
                'id': ctx.guild.id
            }) as cur:
                row = await cur.fetchone()

        desc = [
            "Aeon's Anti-Swear Filter will help protect your server from bad words.",
            f"This feature is currently **{row[1] if row[1] is not None else 'OFF'}**",
            " ",
            f"Users with `Administrator` permissions are ignored.",
            f"Use `{ctx.prefix}{ctx.command} toggle <on/off>` to toggle the filter on or off."
        ]

        blocked = [
            f"||`{row[0] if row[0] is not None else 'Not Set'}`||",
            " ",
            f"Use `{ctx.prefix}{ctx.command} block <words>` to block words.",
            f"Use `,` to separate between words.",
            f"Multiple words in one word `(E.G.: Nigerian Ni**er)` are not supported"
        ]

        log = [
            f"{f'<#{row[2]}>' if row[2] is not None else 'Not Set'}",
            " ",
            f"Use `{ctx.prefix}{ctx.command} log <channel>` to set a channel.",
            f"Use `{ctx.prefix}{ctx.command} log off` to disable."
        ]

        wildcard = [
            f"This feature is currently **{row[3]}**",
            " ",
            f"Use `{ctx.prefix}{ctx.command} wildcard <on/off>` to toggle wildcarding.",
            f"Wildcard removes words that are similar to words in your blocklist.",
            f"For example, Niger would be removed as it similar to Ni**er and is detected by the wildcard."
        ]

        e = discord.Embed(
            title=":gear: Aeon Anti-Swear Filter",
            color=discord.Color.green(),
            description='\n'.join(desc)
        )

        e.add_field(
            name='Blocked Words',
            value='\n'.join(blocked),
            inline=False
        )

        e.add_field(
            name='Log Channel',
            value='\n'.join(log),
            inline=False
        )

        e.add_field(
            name='Wildcarding',
            value='\n'.join(wildcard)
        )

        await ctx.reply(mention_author=False, embed=e)

    @antiswear.command()
    async def block(self, ctx, *, words=None):
        if words is None:
            e = discord.Embed(
                title=':x: Error Blocking Words',
                color=discord.Color.red(),
                description='I need some words to block.'
            )

            await ctx.reply(embed=e, mention_author=False)

        async with connect(self.client.db) as db:
            async with await db.execute(
                    'SELECT swears, delete_swear, log_channel, wildcard FROM config where id = :id',
                    {
                        'id': ctx.guild.id
                    }
            ) as cur:
                row = await cur.fetchone()

            rtstr = 'These words have been blocked in your guild'

            if row[0] is not None:
                await db.execute('UPDATE config SET swears = :words WHERE id = :id', {
                    'id': ctx.guild.id,
                    'words': f"{row[0]}, {words}"
                })
            else:
                await db.execute('UPDATE config SET swears = :words WHERE id = :id', {
                    'id': ctx.guild.id,
                    'words': words
                })

            if words.lower() == 'reset':
                await db.execute('UPDATE config SET swears = :words WHERE id = :id', {
                    'id': ctx.guild.id,
                    'words': 'None'
                })
                rtstr = 'Your blocked words have been reset'

            await db.commit()

        e = discord.Embed(
            title=":white_check_mark: Done",
            color=discord.Color.green(),
            description=rtstr
        )

        await ctx.reply(embed=e)

    @antiswear.command()
    async def wildcard(self, ctx, boolean=None):
        if boolean is None:
            return await self.notice_embeds.error(ctx, "Error setting wildcard!", "No option <on/off> was provided")

        if boolean.upper() in ['ON', 'OFF']:
            async with aiosqlite.connect(self.client.db) as db:
                await db.execute('UPDATE config SET wildcard = :boolean WHERE id = :id', {
                    'id': ctx.guild.id,
                    'boolean': boolean.upper()
                })

                await db.commit()

            e = discord.Embed(
                title=":white_check_mark: Done",
                color=discord.Color.green(),
                description=f"The wildcard is now **{boolean.upper()}**."
            )

        else:
            e = discord.Embed(
                title=':x: Error Setting Wildcard',
                color=discord.Color.red(),
                description='Value can only be ON or OFF.'
            )

        await ctx.reply(embed=e, mention_author=False)

    @antiswear.command()
    async def toggle(self, ctx, boolean=None):
        if boolean is None:
            return await self.notice_embeds.error(ctx, "Error setting anti-swear toggle!", "No option <on/off> was provided")

        if boolean.upper() in ['ON', 'OFF']:
            async with connect(self.client.db) as db:
                await db.execute('UPDATE config SET delete_swear = :boolean WHERE id = :id', {
                    'id': ctx.guild.id,
                    'boolean': boolean.upper()
                })

                await db.commit()

            e = discord.Embed(
                title=":white_check_mark: Done",
                color=discord.Color.green(),
                description=f"The swear filter is now **{boolean.upper()}**."
            )

        else:
            e = discord.Embed(
                title=':x: Error Setting Swear Filter',
                color=discord.Color.red(),
                description='Value can only be ON or OFF.'
            )

        await ctx.reply(embed=e, mention_author=False)

    # Prefix
    @commands.command(brief='Sets the server prefix')
    @commands.has_permissions(manage_messages=True)
    async def prefix(self, ctx, *, prefix=None):
        """
        Changes the prefix for your guild.
        
        If no prefix is provided, it will default to `a!`.
        Prefixes cannot contain a backtick or quotation marks.
        Use `{s}` to add a space at the end of your prefix.
        """

        async with connect(self.client.db) as db:
            cpc = await db.execute('SELECT prefix FROM config WHERE id = :id', {
                'id': ctx.guild.id,
            })
            cp = await cpc.fetchone()
            
            if prefix is None:
                prefix = self.client.prefix

            prefix = prefix \
                .replace('"', "")\
                .replace(" ", "")\
                .replace("`", "")\
                .replace("﷽", "")\
                .replace("'", "")\
                .replace("<@!", "")\
                .replace("<@", "")
            
            if len(prefix) > 15:
                return await self.notice_embeds.error(ctx, "Error Setting Prefix", "This prefix is too long!")
            
            if " " in prefix:
                prefix = prefix.replace(" ", "")

                if prefix.endswith("{s}") and prefix.count("{s}") == 1:
                    prefix = prefix.replace("{s}", " ")

            if prefix in [" ", ""]:
                prefix = self.client.prefix

            if cp:
                await db.execute('UPDATE config SET prefix = :prefix WHERE id = :id', {
                    'id': ctx.guild.id,
                    'prefix': prefix
                })
            else:
                await db.execute('INSERT INTO config (id, prefix) VALUES (:id, :prefix)', {
                    'id': ctx.guild.id,
                    'prefix': prefix
                })

            e = discord.Embed(
                title=":white_check_mark: Prefix Set",
                description=f"My prefix in this server is now `{prefix}`.",
                color=discord.Color.green()
            )

            await ctx.reply(embed=e, mention_author=None)
            await db.commit()


def setup(client):
    client.add_cog(Config(client))
