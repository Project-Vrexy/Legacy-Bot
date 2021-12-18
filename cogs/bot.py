# StdLib
from platform import system, release, version
import sys
import asyncio
from re import sub
from time import perf_counter
from datetime import datetime

# Discord
import nextcord as discord
from nextcord.ext import commands
from dislash import SelectMenu, SelectOption

# Third Party
import psutil
from hurry.filesize import size
from difflib import SequenceMatcher
from ujson import load

# Local Code
from cogs.utils.uptimer import Uptimer
from cogs.utils.embeds import EmbedUtils, NoticeEmbeds
from cogs.utils.help import HelpUtils, HelpMenus
from cogs.utils.paginator import Paginator
from cogs.utils.custom_checks import WaitForChecks


# noinspection PyTypeChecker
class Bot(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.emoji = '🤖'
        self.desc = 'Commands that display info about Aeon'

        self.uptimer = Uptimer(datetime.now())
        self.embed_utils = EmbedUtils(client)
        self.notice_embeds = NoticeEmbeds(client)
        self.help_utils = HelpUtils(client)
        self.help_menus = HelpMenus(client)

        self.invite_url = "https://discord.com/api/oauth2/authorize?client_id=id&permissions=8&scope=bot%20applications.commands"
        self.support_url = "https://discord.gg/bCkZ2dF5Sm"
        self.website_url = "https://aeonbot.xyz"
        self.vote_url = "https://top.gg/bot/636991807862997000/vote"

        self.extras = {
            "say": {
                "examples": [
                    "PlaceDet Hello, I am Aeon!",
                    "PlaceDet Hello, I am Aeon! -d"
                ]
            }
        }

    # Help: General
    @commands.command(name="help", brief="Displays this message.", usage='[command]')
    async def _help(self, ctx, command=None):
        is_nsfw = ctx.channel.is_nsfw() if ctx.guild is not None else False
        check_required = ["Nsfw", "Music", "Economy"]

        if command:
            new_command = self.client.get_command(name=command.lower())

            if new_command not in self.client.commands:
                suggestion = None
                t = "Command Does Not Exist"

                for client_command in self.client.all_commands:
                    if self.client.all_commands[client_command].enabled and not \
                            self.client.all_commands[client_command].hidden:
                        ratio = round(SequenceMatcher(a=command.lower(), b=client_command).ratio(), 1)

                        if ratio >= 0.7:
                            suggestion = client_command
                            break

                if suggestion is None:
                    return await self.notice_embeds.error(ctx, t, "Please try again and check your spelling")
                else:
                    return await self.notice_embeds.error(ctx, t,
                                                          "Perhaps you meant to find info on "
                                                          f"`{ctx.prefix}{ctx.command} {suggestion}`?")
            elif new_command.hidden:
                return await self.notice_embeds.error(ctx, f"Command is Disabled",
                                                      f"I can't get info on that command as it is disabled.")
            elif new_command.enabled is False:
                return await self.notice_embeds.error(ctx, f"Command is Hidden",
                                                      f"I can't get info on that command as it is hidden.")
            elif new_command.cog_name == "Nsfw" and is_nsfw is False:
                ne = discord.Embed(
                    title=":no_entry: Command is NSFW",
                    color=discord.Color.red(),
                    description="You can only view info on NSFW commands in NSFW channels."
                )

                ne.set_image(url="https://i.imgur.com/oe4iK5i.gif")
                return await ctx.reply(mention_author=False, embed=ne)

            ie = discord.Embed(
                title=":question: Aeon Help",
                color=discord.Color.green(),
                description=f"**{new_command.name.title()}**\n"
                            f"{new_command.brief if new_command.help is None else new_command.help}"
            )

            ie.set_footer(text='<> - Required. [] - Optional')
            ie.add_field(name="Category", value=new_command.cog_name.replace('Nsfw', 'NSFW'))

            if new_command.aliases:
                aliases = []
                for alias in new_command.aliases:
                    aliases.append(alias.upper())

                aliases.sort()
                ie.add_field(name="Aliases", value=', '.join(new_command.aliases))

            if new_command.usage:
                ie.add_field(name="Usage", value=await self.help_utils.get_command_usage(ctx, new_command,
                                                                                         return_usage=True))

            if new_command.description:
                await self.help_utils.examples(context=ctx, embed=ie, command=new_command)

            await self.help_utils.get_clean_checks(ctx, new_command, embed=ie)
            await self.help_utils.get_required_env(ctx, new_command, embed=ie)

            return await ctx.reply(embed=ie)

        he = discord.Embed(
            title=":question: Aeon Help",
            color=discord.Color.green(),
            description='\n'.join([
                f"For more help and support, join the [support server](https://discord.gg/tuCpWgn5W8/).",
                f"`{ctx.prefix}{ctx.command} [command]` views info about a command."
            ])
        )

        he.add_field(name="\u200b",
                     value="**:information_source: No category picked**\nYou have not yet picked a category to view.",
                     inline=False)

        commands_for_everyone = []
        commands_for_a_few = []

        for listed_cog in self.client.cogs:
            cog = self.client.get_cog(listed_cog)

            def append(command_list):
                command_list.append({
                    'emoji': cog.emoji,
                    'name': cog.__class__.__name__,
                    'desc': cog.desc
                })

            if 'emoji' in dir(cog):
                if 'not_everyone' not in dir(cog):
                    if cog.__class__.__name__ in check_required:
                        if cog.__class__.__name__ == "Nsfw" and is_nsfw is True:
                            append(commands_for_everyone)
                        elif cog.__class__.__name__ in ["Music", "Economy"] and ctx.guild is not None:
                            append(commands_for_everyone)
                    else:
                        append(commands_for_everyone)
                else:
                    append(commands_for_a_few)
            else:
                continue

        cogs_count = len(commands_for_everyone) + len(commands_for_a_few) if ctx.guild is not None else \
            len(commands_for_everyone)
        cmds_count = sum(bool(command.enabled and not command.hidden) for command in self.client.commands)
        he.set_footer(text=f"{cmds_count} commands | {cogs_count} Categories")

        select_menu_options = [SelectOption(label=cog['name'], value=cog['name'], description=cog['desc'],
                                            emoji=cog['emoji']) for cog in commands_for_everyone]
        if ctx.guild:
            few_list = [SelectOption(label=cog['name'], value=cog['name'], description=cog['desc'],
                                     emoji=cog['emoji']) for cog in commands_for_a_few]
            select_menu_options.extend(few_list)
        select_menu_options.sort(key=lambda x: x.label)

        msg = await ctx.reply(
            embed=he,
            components=[
                SelectMenu(placeholder="Pick a category", options=select_menu_options)
            ],
            mention_author=False
        )

        wait_check = WaitForChecks(self.client, ctx)
        while True:
            try:
                res = await msg.wait_for_dropdown(wait_check.aligned_ctx, None)
            except asyncio.TimeoutError:
                return await msg.edit(embed=he, components=[])

            cog = res.select_menu.selected_options[0].label
            filtered_commands = [cmd.name for cmd in self.client.commands if not cmd.hidden and cmd.enabled and
                                 cmd.cog_name == cog.capitalize()]

            cog_info = self.client.get_command(name=filtered_commands[0])
            filtered_commands.sort()

            split_commands = await self.help_utils.page_split(filtered_commands, 5)
            pages = []

            n = '\n'

            for page, command_chunk in enumerate(split_commands, start=1):
                e = discord.Embed(
                    title=":question: Aeon Help",
                    color=discord.Color.green(),
                    description=f"**{cog_info.cog.emoji} "
                                f"{cog_info.cog_name.replace('Nsfw', 'NSFW')}**\n{cog_info.cog.desc}."
                )

                for listed_command in command_chunk:
                    command = self.client.get_command(name=listed_command)
                    help_str = []

                    checks = await self.help_utils.get_clean_checks(ctx, command)
                    if checks:
                        help_str.append(checks)

                    enved = await self.help_utils.get_required_env(ctx, command)
                    if enved:
                        help_str.extend(enved)

                    e.add_field(
                        name=f"`{await self.help_utils.get_command_signature(ctx, command, True)}`",
                        value=f"```yaml\n{command.brief}```{n.join(help_str)}", inline=False
                    )

                e.set_footer(text=f"<> - Required • [] - Optional. "
                                  f"\nPage {page}/{len(split_commands)} • "
                                  f"{len(command_chunk)}/{len(filtered_commands)} Commands.")

                pages.append(e)

            paginator = Paginator(self.client, ctx, pages)
            await paginator.replace(message=msg, orig_comp=[
                SelectMenu(placeholder="Pick a category", options=select_menu_options)
            ], orig_embed=he)
            await res.reply(type=6)

    # --------------------------------

    # Changelog
    @commands.command(brief='View what\'s been added to the bot.')
    async def changelog(self, ctx):
        with open(f"{self.client.json}/changelog.json") as changelog:
            changes = load(changelog)

        e = discord.Embed(
            title=':information_source: What\'s New in Aeon',
            color=discord.Color.green(),
            description="Check <#822391869714464798> in the support server for a list of all changelogs."
        )

        s = '\n'
        for change in changes:
            total_section = ""
            for count, section in enumerate(change['changes']):
                if count == 0:
                    total_section += f"**{section['title']}**\n{s.join(section['changes'])}"
                else:
                    total_section += f"\n\n**{section['title']}**\n{s.join(section['changes'])}"

            e.add_field(
                name=f"__{change['date']} ({change['version']})__",
                value=total_section,
                inline=False
            )

        await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # About
    @commands.command(aliases=['info', 'links', 'invite', 'vote'], brief="Information about the bot.")
    async def about(self, ctx):
        devs = ["<@348591272476540928>"]
        admins = ["<@603635602809946113>"]
        thanks = ["<@444550944110149633>", "<@429935667737264139>"]

        stats = [
            f"**:calling: Commands:** {len(self.client.commands)} commands",
            f"**:homes: Guilds:** {len(self.client.guilds)} guilds",
            f"**:busts_in_silhouette: Users:** {len(self.client.users)} users",
            f"**:ping_pong: Ping:** {round(self.client.latency * 1000)}ms",
        ]

        links = [
            f":incoming_envelope: [Invite Link]({self.invite_url.replace('=id', f'={self.client.user.id}')})",
            f":question: [Support Server]({self.support_url})",
            f":globe_with_meridians: [Website]({self.website_url})",
            f":ballot_box: [Vote]({self.vote_url})",
        ]

        e = discord.Embed(
            title=":information_source: About Aeon",
            color=discord.Color.green(),
            description="A multi-purpose bot that does stuff like memes, tags, reminders, and anti-swear filtering."
        )

        e.add_field(name="<:bot_dev:836605174696509471> Developers", value='\n'.join(devs))
        e.add_field(name=":police_officer: Bot Admins", value='\n'.join(admins))
        e.add_field(name=":star: Special Thanks", value='\n'.join(thanks))

        e.add_field(name=":bar_chart: Stats", value='\n'.join(stats))
        e.add_field(name=":link: Links", value='\n'.join(links))

        e.set_thumbnail(url=self.client.user.display_avatar.url)

        with open(f"{self.client.json}/changelog.json") as changelog:
            changes = load(changelog)

        e.set_footer(text=f"Aeon {changes[0]['version']} using Nextcord {discord.__version__} "
                          f"with Python {sys.version.split(' (')[0]}")
        await ctx.reply(mention_author=False, embed=e)

    # System
    @commands.command(brief="View the information of the host server/computer")
    async def system(self, ctx):
        e = discord.Embed(
            title=":gear: Host System Information",
            color=discord.Colour.green()
        )

        await self.embed_utils.field_title(e, "**:brain: CPU**")
        e.add_field(name="CPU Usage", value=str(psutil.cpu_percent()) + "%")
        e.add_field(name="Logical CPU Count", value=psutil.cpu_count())

        mem = psutil.virtual_memory()
        await self.embed_utils.field_title(e, "**:floppy_disk: Memory**")
        used = str(size(mem.total - mem.available))

        e.add_field(name="Total Memory", value=size(mem.total) + "B")
        e.add_field(name="Used Memory", value=f"{used}B")
        e.add_field(name="Available Memory", value=size(mem.available) + "B")
        e.add_field(name="Memory Usage", value=str(mem.percent) + "%")

        disk = psutil.disk_usage("/")
        await self.embed_utils.field_title(e, "**:minidisc: Disk**")

        e.add_field(name="Total Space", value=size(disk.total) + "B")
        e.add_field(name="Used Space", value=size(disk.used) + "B")
        e.add_field(name="Free Space", value=size(disk.free) + "B")
        e.add_field(name="Disk Usage", value=str(disk.percent) + "%")

        net = psutil.net_io_counters()
        await self.embed_utils.field_title(e, "**:satellite: Network**")

        e.add_field(name="Packets Sent", value=net.packets_sent)
        e.add_field(name="Packets Received", value=net.packets_recv)
        e.add_field(name="Bytes Sent", value=size(net.bytes_sent) + "B")
        e.add_field(name="Bytes Received", value=size(net.bytes_recv) + "B")

        await self.embed_utils.field_title(e, "**:penguin: OS**")
        e.add_field(name="System", value=system())
        e.add_field(name="Release", value=release() if len(release()) > 0 else "???")
        e.add_field(name="Version", value=version() if len(version()) > 0 else "???")

        await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Uptime
    @commands.command(brief="Get the uptime of the bot")
    async def uptime(self, ctx):
        e = discord.Embed(
            title=":clock3: Aeon Uptime",
            color=discord.Color.green(),
            description=f"**:white_small_square: Bot:** {self.uptimer.get_bot_uptime()}"
            f"\n**:white_small_square: System:** {self.uptimer.get_sys_uptime()}"
        )

        await ctx.reply(mention_author=False, embed=e)

    # Ping
    @commands.command(brief="Shows the bot ping.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def ping(self, ctx):
        async with ctx.channel.typing():
            t1 = perf_counter()
            await ctx.trigger_typing()
            t2 = perf_counter()
            res = round((t2 - t1) * 1000)

        e = discord.Embed(
            title=":ping_pong: Pong!",
            description=f":white_small_square: Bot Latency: **{round(self.client.latency * 1000)}**ms"
                        f"\n:white_small_square: API Latency: **{res}**ms",
            color=discord.Color.green()
        )

        await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Say
    @commands.command(brief="The bot says whatever you tell it to.", usage="<text")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def say(self, ctx, *, parameter: str):
        """
        Says whatever you input after the command.

        Add `-d` at the end of your message if you want Aeon automatically delete your message.
        """

        if parameter.lower().endswith("-d"):
            parameter = parameter.replace("-d", "").replace("-D", "")
            await ctx.message.delete()

        swears = ['nigger', 'nigga', '@everyone', '@here', 'tranny', 'g', 'sexo', 'gatos', 'tiene']
        sayable_item = []

        for word in parameter.split(" "):
            sayable_item.append('[REMOVED]') if sub(r'\W+', '', word.lower()) in swears else sayable_item.append(word)

        return await ctx.send(discord.utils.escape_mentions(' '.join(sayable_item)))
    
    # Dashboard
    @commands.command(brief="Access the dashboard page for your server.")
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def dashboard(self, ctx):
        e = discord.Embed(title="Aeon Dashboard", description="[Click here to access your dashboard edit page!]("
                                                              "https://aeonbot.xyz/dashboard/edit/?server="
                                                              f"{ctx.guild.id})", color=discord.Colour.green())
        e.set_thumbnail(url=self.client.user.avatar.url)
        await ctx.reply(embed=e)


def setup(client):
    client.add_cog(Bot(client))
