# Discord
import nextcord as discord
from nextcord.ext import commands

# Local Code
from cogs.utils import embeds
from cogs.utils import help
from cogs.utils.paginator import Paginator


class Meta(commands.Cog):
    def __init__(self, client):
        self.client = client
 
        self.emoji = '🖥️'
        self.desc = 'Commands related to Discord itself'

        self.extras = {
            'permissions': {
                'guild_only': True
            },
            'roles': {
                'guild_only': True
            },
            'guildinfo': {
                'guild_only': True
            },
            'channelinfo': {
                'guild_only': True
            },
            'ei': {
                'examples': [
                    "PlaceDet :the:"
                ]
            },
            'enlarge': {
                'examples': [
                    "PlaceDet :the:"
                ]
            }
        }

        self.embed_utils = embeds.EmbedUtils(client)
        self.help_utils = help.HelpUtils(client)
        self.notice_embeds = embeds.NoticeEmbeds(client)

    # Avatar
    @commands.command(brief='Get a user\'s avatar.', usage='[user]', aliases=["pfp", "icon"])
    async def avatar(self, ctx, user: discord.Member = None):
        """
        Gets the icon of the specified user.

        If no user is provided, it will default to the author of the message."""

        if user is None:
            user = ctx.author

        e = discord.Embed(
            title=f":frame_photo: Avatar of {user.name}",
            color=user.top_role.color,
            url=f"{user.display_avatar.url}")

        e.set_image(url=user.display_avatar.url)
        await ctx.reply(mention_author=False, embed=e)

    # User Info
    @commands.command(brief="Get info on a user.", usage="[user]", aliases=["ui", "user-info"])
    async def userinfo(self, ctx, user: discord.Member = None):
        """Gets information on the specified user.

        If no user is provided, it will default to the author of the message.
        """

        if user is None:
            user = ctx.author

        e = discord.Embed(
            title=f":information_source: User Info of {user}",
            color=user.top_role.color if ctx.guild is not None else discord.Color.green()
        )

        e.add_field(name="User ID", value=user.id)
        e.add_field(name="Name", value=user.display_name)
        e.add_field(name="Account Created", value=str(user.created_at)[:-7])

        if ctx.guild is not None:
            e.add_field(name="Roles", value=f"{len(user.roles) - 1}/{len(ctx.guild.roles) - 1}")
            e.add_field(name="Joined Server", value=str(user.joined_at)[:-7])
            e.add_field(name="Highest Role", value=f"<@&{user.top_role.id}>")

            await self.embed_utils.field_title(e, "<:NextPage:860504617984196618> - Permissions")

        e.set_thumbnail(url=user.display_avatar.url)

        pages = [e]

        if ctx.guild is not None:
            e2 = discord.Embed(
                title=f"User Permissions of {user}",
                color=user.top_role.color
            )

            ap = [
                x.replace('_', ' ').title().replace('Tts', 'TTS')
                for x in dir(user.guild_permissions)
                if getattr(user.guild_permissions, x) is True
            ]

            dp = [
                x.replace('_', ' ').title().replace('Tts', 'TTS')
                for x in dir(user.guild_permissions)
                if getattr(user.guild_permissions, x) is False
            ]

            ap.sort()
            dp.sort()

            if len(ap) != 0:
                e2.add_field(name=":white_check_mark: Allowed Permissions", value="\n".join(ap))

            if len(dp) != 0:
                e2.add_field(name=":no_entry: Disallowed Permissions", value="\n".join(dp))

            await self.embed_utils.field_title(e2, "<:PreviousPage:860504570734837790> - Info. "
                                                   "<:NextPage:860504617984196618> - Roles")
            e2.set_thumbnail(url=user.display_avatar.url)

            roles = []
            for role in user.roles:
                if role.name == "@everyone":
                    roles.append(f"@everyone")
                else:
                    roles.append(f"<@&{role.id}>")

            e3 = discord.Embed(
                title=f"Roles of {user}",
                color=user.top_role.color,
                description='\n'.join(roles) if roles else 'No Roles'
            )

            await self.embed_utils.field_title(e3, "<:PreviousPage:860504570734837790> - Permissions")
            e3.set_thumbnail(url=user.display_avatar.url)

            pages.append(e2)
            pages.append(e3)

        paginator = Paginator(self.client, ctx, pages)
        await paginator.run()

    # --------------------------------

    # Guild Info
    @commands.guild_only()
    @commands.command(brief="View info on the current guild.",
                      aliases=["gi", "guild-info", "si", "severinfo", "server-info"])
    async def guildinfo(self, ctx):
        e = discord.Embed(
            title=f":information_source: {ctx.guild.name}",
            description=ctx.guild.description or None,
            color=discord.Color.green(),
        )

        vc = []
        tc = []
        for channel in ctx.guild.channels:
            if isinstance(channel, discord.TextChannel):
                tc.append(channel.name)
            elif isinstance(channel, discord.VoiceChannel):
                vc.append(channel.name)

        gf = [
            feature.replace("_", " ").title().replace("Vip", "VIP")
            for feature in ctx.guild.features
        ]

        channels = len(vc) + len(tc)

        e.add_field(name="ID", value=ctx.guild.id)
        e.add_field(name="Owner", value=ctx.guild.owner)
        e.add_field(name="Channels", value=f"{channels} ({len(tc)} text, {len(vc)} voice)")
        e.add_field(name="Creation Date", value=str(ctx.guild.created_at)[:-7])
        e.add_field(name="Role Count", value=f"{len(ctx.guild.roles)} roles")
        e.add_field(name="Member Count", value=f"{len(ctx.guild.members)} members")
        e.add_field(
            name="Rules Channel",
            value=f"<#{ctx.guild.rules_channel.id}>" if ctx.guild.rules_channel else 'None'
        )

        e.add_field(name="Features", value=', '.join(gf) if gf else 'No Features')

        e.set_thumbnail(url=ctx.guild.icon.url)

        if ctx.guild.banner:
            e.set_image(url=ctx.guild.banner.url)

        return await ctx.reply(embed=e, mention_author=False)

    # Channel Info
    @commands.guild_only()
    @commands.command(brief="View info on the current channel or a specified channel.", aliases=["ci", "channel-info"])
    async def channelinfo(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            channel = ctx.channel

        get_rules = ctx.guild.rules_channel or None

        if get_rules is not None and get_rules.id == channel.id:
            is_rules = "Yes"
        else:
            is_rules = "No"

        e = discord.Embed(
            title=f":information_source: #{channel.name}",
            color=discord.Color.green(),
            description=channel.topic or None,
        )

        await self.embed_utils.field_title(e, "General")
        e.add_field(name="ID", value=channel.id)
        e.add_field(name="Created At", value=str(channel.created_at)[:-7])

        await self.embed_utils.field_title(e, "Types")
        e.add_field(name="Announcements?", value="Yes" if channel.is_news() else "No")
        e.add_field(name="NSFW?", value="Yes" if channel.is_nsfw() else "No")
        e.add_field(name="Rules?", value=is_rules)

        if channel.category is not None:
            await self.embed_utils.field_title(e, "Category Info")
            e.add_field(name="Category", value=channel.category.name)
            e.add_field(name="Category ID", value=channel.category_id)

        await self.embed_utils.field_title(e, "Other")
        e.add_field(name="Position", value=str(channel.position))
        e.add_field(name="Slowmode", value=str(channel.slowmode_delay))

        await ctx.reply(embed=e, mention_author=False)

    # Oldest User
    @commands.guild_only()
    @commands.command(brief="Views the oldest user(s) in the server.", usage="<show bots (yes/no)> <show one user ("
                                                                             "yes/no)>")
    async def oldest(self, ctx, include_bots, show_one_user):
        def boolstr(to_bool):
            if to_bool.lower() in ['yes', 'no']:
                if to_bool.lower() == 'yes':
                    return True
                else:
                    return False
            else:
                return None

        include_bots = boolstr(include_bots)
        show_one_user = boolstr(show_one_user)

        if None in [show_one_user, include_bots]:
            return await self.notice_embeds.error(ctx, "Error Listing Users", "One of your options was not yes or no.")

        if include_bots:
            time = [(user, str(user.created_at)[:-16]) for user in ctx.guild.members]
        else:
            time = [(user, str(user.created_at)[:-16]) for user in ctx.guild.members if not user.bot]

        time.sort(key=lambda x: x[1].split(" ")[0])

        if show_one_user:
            e = discord.Embed(
                title=":drum: And the oldest user is...",
                description=f"**{str(time[0][0])}**\nCreated at {time[0][1].split(' ')[0]}\nCongratulations, "
                            f"<@{time[0][0].id}>",
                color=time[0][0].top_role.color
            )
            e.set_thumbnail(url=time[0][0].display_avatar.url)
            await ctx.reply(embed=e, mention_author=False)
        else:
            chunk = await self.help_utils.page_split(time, 10)
            chunk = chunk[0]

            e = discord.Embed(title=":drum: And the oldest users are...", color=discord.Color.green())

            for user in chunk:
                e.add_field(name=str(user[0]), value=f"Created at {user[1].split(' ')[0]}", inline=False)

            await ctx.reply(embed=e, mention_author=False)
    # --------------------------------

    # Emoji Info
    @commands.command(brief="View info on a custom emoji.", aliases=["emojiinfo", "emoji-info"], usage="<custom emoji>")
    async def ei(self, ctx, emoji: discord.PartialEmoji):
        e = discord.Embed(
            title=f"{emoji}'s info",
            color=discord.Color.green()
        )

        e.add_field(name="Emoji Name", value=f"`:{emoji.name}:`")
        e.add_field(name="Emoji ID", value=emoji.id)
        e.add_field(name="Animated", value=emoji.animated)
        e.add_field(name="Emoji URL", value=f"[URL]({emoji.url})")
        e.add_field(name="Created At", value=str(emoji.created_at)[:-7])

        e.set_thumbnail(url=emoji.url)
        await ctx.reply(embed=e, mention_author=False)

    # Enlarge
    @commands.command(brief='Enlarges an emoji')
    async def enlarge(self, ctx, emoji: discord.PartialEmoji):
        e = discord.Embed(
            title=f":frame_photo: {emoji.name}",
            color=discord.Color.green()
        )

        e.set_image(url=f"{emoji.url}?v=1&size=4096")
        await ctx.reply(embed=e, mention_author=False)


def setup(client):  
    client.add_cog(Meta(client))
