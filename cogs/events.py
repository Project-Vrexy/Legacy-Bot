# StdLib
import asyncio
from asyncio import sleep
import os
import platform
import re
from sys import stderr
from traceback import format_exception
from datetime import datetime

# Discord
import nextcord as discord
from nextcord.ext import commands

# Third Party
from difflib import SequenceMatcher
import aiosqlite
import ujson as json

# Local Code
from cogs.utils import errors
from cogs.utils.embeds import NoticeEmbeds
from cogs.utils.help import HelpUtils


# Cog
class Events(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.start = datetime.now()
        self.notice_embeds = NoticeEmbeds(client)
        self.help_utils = HelpUtils(client)

        client.add_check(self.block_users)
        client.add_check(self.per_guild_command_disabling)

    # Bot: On Connect
    @commands.Cog.listener()
    async def on_connect(self):
        print(" \n==== Bot ====")
        print(f"{self.client.user}: Connected\n ")

    # Bot: On Ready
    @commands.Cog.listener()
    async def on_ready(self):
        # Print
        print(f'{self.client.user}: Ready')

        # Setup Presence
        await self.client.change_presence(status=discord.Status.idle)
        await self.client.change_presence(activity=discord.Activity(type=2, name=f"{self.client.prefix}help・"
                                                                                 "aeonbot.xyz"))
        end = datetime.now()
        print(f"{self.client.user}: Booted in {str(end - self.start)[6:12]}s")

        # Process Started Logs
        channel = self.client.get_channel(826732008805236737)
        now = datetime.now()

        e = discord.Embed(
            title="<:online:747395937625833552> Process Started",
            color=discord.Color.green(),
            description=f"**Process started at:** {now.strftime('%Y/%m/%d %H:%M:%S')}"
        )

        await channel.send(embed=e)

    # Bot: Disconnect
    @commands.Cog.listener()
    async def on_disconnect(self):
        print('Bot: Disconnected')

    # --------------------------------

    # Shards: On Shard Connect
    @commands.Cog.listener()
    async def on_shard_connect(self, shard_id):
        print(f'     ==== Shard {shard_id} ====')
        print(f"     Shard {shard_id}: Connected")

    # Shards: On Shard Ready
    @commands.Cog.listener()
    async def on_shard_ready(self, shard_id):
        print(f"     Shard {shard_id}: Ready\n ")

    # Shards: On Shard Disconnect
    @commands.Cog.listener()
    async def on_shard_disconnect(self, shard_id):
        print(f"Shard {shard_id}: Disconnected")

    # --------------------------------

    # Guilds: On Guild Join
    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        with open(f"{self.client.json}/blocked.json") as blocklist:
            bl_data = json.load(blocklist)

        if guild.owner.id in bl_data['users']:
            await guild.leave()
            return
            
        # Logs
        channel = self.client.get_channel(826720686918991912)

        join = discord.Embed(
            title="Aeon Joined a Server",
            color=discord.Colour.green(),
            timestamp=datetime.now().astimezone()
        )

        join.add_field(name="ID", value=guild.id)
        join.add_field(name="Owner", value=guild.owner)
        join.add_field(name="Members", value=f"{len(guild.members)} ({len([x for x in guild.members if x.bot])} bots)")
        
        if guild.icon:
            join.set_thumbnail(url=guild.icon.url)

        join.set_author(name=guild.name,
                        icon_url='https://images-ext-1.discordapp.net/external/' +
                                 'GVopI332P9PhUbxevgRIDBudDpGeDAw1mueTbkDijno/https/i.ibb.co/YP7WMxF/joined.png')
        join.set_footer(text=f"Aeon is now in {len(self.client.guilds)} servers")

        await channel.send(embed=join)

        async with aiosqlite.connect(self.client.db) as db:
            await db.execute(
                'INSERT INTO config VALUES (:id, :ds, :swears, :lc, :wc, :suggest, :prefix, :pe, :dc)',
                {
                    'id': int(guild.id),
                    'ds': 'OFF',
                    'swears': None,
                    'lc': None,
                    'wc': 'OFF',
                    'suggest': None,
                    'prefix': self.client.prefix,
                    'pe': None,
                    'dc': None
                }
            )
            await db.commit()

    # Guilds: On Guild Remove
    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        if not guild.name:
            return       
        channel = self.client.get_channel(826720686918991912)

        remove = discord.Embed(
            title="Aeon Left a Server",
            color=discord.Colour.green(),
            timestamp=datetime.now().astimezone()
        )

        remove.add_field(name="ID", value=guild.id)
        remove.add_field(name="Owner", value=guild.owner)
        remove.add_field(name="Members",
                         value=f"{len(guild.members)} ({len([x for x in guild.members if x.bot])} bots)")
        remove.set_author(name=guild.name,
                          icon_url='https://images-ext-1.discordapp.net/external/' +
                                   'atqx8jqLNvBzptRfTjfD11Lq0-7NGjrJonXXImuiodE/https/i.ibb.co/mcPyC2r/left.png')
        if guild.icon:
            remove.set_thumbnail(url=guild.icon.url)
        
        remove.set_footer(text=f"Aeon is now in {len(self.client.guilds)} servers")

        await channel.send(embed=remove)

        async with aiosqlite.connect(self.client.db) as db:
            await db.execute('DELETE FROM config WHERE id = :id', {
                'id': guild.id
            })
            try:
                await db.execute('DELETE FROM disabled WHERE id = :id', {'id': guild.id})
            except aiosqlite.OperationalError:
                pass
            
            try:
                for channel in guild.channels:
                    await db.execute('DELETE FROM snipes WHERE channel_id = :channel_id', {
                        'channel_id': channel.id
                    })
            except aiosqlite.OperationalError:
                pass

            await db.commit()

    # --------------------------------

    # Messages: On Message
    @commands.Cog.listener()
    async def on_message(self, message):
        # Self Return
        if message.author == self.client.user:
            return
        
        # Remove Github Action Checks
        if message.channel.id == 826727124982562866 and "github actions" in message.embeds[0].title.lower():
            await message.delete()
        
        # Execute Everywhere
        if message:
            if "discord.com/channels" in message.content:
                split_msg = message.content.replace("https://", " ").split("/")

                channel = await self.client.fetch_channel(split_msg[3])
                msg = await channel.fetch_message(re.sub(r'\W+', '', split_msg[4].split(" ")[0]))

                if msg.embeds:
                    return

                e = discord.Embed(
                    description=msg.content,
                    color=msg.author.top_role.color if msg.guild else discord.Color.green(),
                    timestamp=msg.created_at
                )

                if msg.guild:
                    e.add_field(name="Server", value=msg.guild.name)

                e.add_field(name="Channel", value=f"<#{split_msg[3]}>")

                e.set_author(name=f"{str(msg.author)}", icon_url=msg.author.display_avatar.url)
                await message.channel.send(embed=e)

        # Execute in DMs
        if message.guild is None:
            return

        # Execute in guilds
        if message.guild is not None:
            async with aiosqlite.connect(self.client.db) as db:
                async with await db.execute(
                        'SELECT swears, delete_swear, log_channel, wildcard FROM config where id = :id',
                        {
                            'id': message.guild.id
                        }
                ) as cur:
                    row = await cur.fetchone()

                    if row is None:
                        return

                    # Should Delete Swears?
                    delete_swear = True if row[1] == 'ON' else False

                    if row[0] is None:
                        delete_swear = False

                    # What Do I Remove?
                    if row[0] is not None:
                        swears = row[0].split(', ')

                    channel = self.client.get_channel(int(row[2])) if row[2] is not None else None

                    # Do you want more remove
                    wildcard = True if row[3] == 'ON' else False

                    try:
                        admin = message.author.guild_permissions.administrator and not message.author.bot
                    except AttributeError:
                        admin = False

                    async def swear_detected(log):
                        try:
                            await message.delete()
                        except discord.NotFound:
                            pass

                        embed = discord.Embed(
                            title=":warning: Check your language!",
                            color=discord.Color.gold(),
                            description="You can't say that word!"
                        )

                        swear_notice = await message.channel.send(f"{message.author.mention},", embed=embed)

                        if log is not None:
                            embed = discord.Embed(
                                title=":warning: User Swore",
                                color=discord.Color.gold(),
                                description=message.content
                            )

                            embed.add_field(name='Message ID', value=message.id)
                            embed.add_field(name='User', value=f"<@{message.author.id}> ({message.author.id})")
                            embed.add_field(name='Channel', value=f"<#{message.channel.id}> ({message.channel.id})")
                            await log.send(embed=embed)

                        await sleep(5)
                        try:
                            await swear_notice.delete()
                        except discord.NotFound:
                            pass

                    if delete_swear is True:
                        for word in message.content.split():
                            if re.sub(r'\W+', '', word.lower()) in swears and admin is False:
                                await swear_detected(log=channel)
                            else:
                                for swear in swears:
                                    ratio = round(
                                        number=SequenceMatcher(
                                            a=re.sub(r'\W+', '', word.lower()),
                                            b=swear
                                        ).ratio(),
                                        ndigits=1
                                    )

                                    if ratio >= 0.8 and admin is False and wildcard is True:
                                        await swear_detected(log=channel)

                async with await db.execute(
                    'SELECT prefix, prefix_warn FROM config where id = :id', {'id': message.guild.id}
                ) as cur:
                    mc = message.content
                    scui = self.client.user.id
                    scp = self.client.prefix

                    row = await cur.fetchone()
                    gp = row[0] if row[0] is not None else self.client.prefix
                    gpw = True if row[1] is not None else False

                    if gp != scp and gpw is True and message.content.startswith(scp):
                        e = discord.Embed(
                            title=":flushed: Well, that's embarrassing",
                            description=f"My prefix in this server is `{gp}`, use that!",
                            color=discord.Color.gold()
                        )

                        await message.reply(embed=e, mention_author=False)

                    if mc.startswith(f"<@{scui}>") or mc.startswith(f"<@!{scui}>") and len(mc.split(" ")) == 1:
                        e = discord.Embed(
                            title=":question: What the hell is this thing's prefix?",
                            description=f"My prefix in this server is `{gp}`.",
                            color=discord.Color.green()
                        )

                        await message.reply(embed=e, mention_author=False)

    # Messages: On Message Delete
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author == self.client.user or message.author.bot:
            return

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute(
                    'SELECT * FROM snipes WHERE channel_id = :id',
                    {
                        'id': message.channel.id
                    }
            ) as cur:
                record = await cur.fetchone()

            if record is not None:
                query = "UPDATE snipes SET user_id = :user, text = :text, time = :time WHERE channel_id = :channel"
            else:
                query = "INSERT INTO snipes VALUES (:channel, :user, :text, :time)"

            await db.execute(query, {
                'channel': message.channel.id,
                'user': message.author.id,
                'text': message.content,
                'time': datetime.now()
            })

            await db.commit()

    # --------------------------------

    # Commands: Blacklist
    async def block_users(self, ctx):
        with open(f"{self.client.json}/blocked.json", "r") as f:
            blacklist = json.load(f)

        if ctx.author.id in set(blacklist['users']):
            raise errors.UserIsBlacklisted()
        else:
            return True

    # Commands: Guild Disabled Command
    async def per_guild_command_disabling(self, ctx):
        if ctx.guild is None:
            return True
        
        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute('SELECT disabled_commands FROM config WHERE id = :id', {'id': ctx.guild.id}) \
                    as cur:
                row = await cur.fetchone()

        if row is None or None in row:
            return True
        else:
            disabled_commands = row[0].split(", ")

        if ctx.command.name in set(disabled_commands):
            raise errors.GuildDisabledCommand()
        else:
            return True

    # Commands: On Command Error
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        # Commands: BlackListedUser
        if isinstance(error, errors.UserIsBlacklisted):
            return await self.notice_embeds.no_perms(ctx, "Access Denied", "You are blacklisted from using Aeon.")
        
        blocked = [discord.HTTPException, discord.NotFound, errors.DeafError, asyncio.TimeoutError]

        if ctx.command:
            cog = ctx.command.cog
            command = ctx.command

            if cog.has_error_handler():
                blocked.extend(cog.cog_error_handler_slots)
            elif command.has_error_handler():
                slots = cog.command_error_handler_slots[command.name] if not command.parent else \
                    cog.command_error_handler_slots[command.parent.name][command.name]

                blocked.extend(slots)

        # Errors: Blocked Errors
        if isinstance(error, tuple(blocked)):
            return

        # Commands: CommandOnCooldown
        elif isinstance(error, commands.CommandOnCooldown):
            cooldown = round(error.retry_after, 2)
            time = "second" if cooldown == 1 else "seconds"

            return await self.notice_embeds.no_perms(ctx, "Too Fast", "You'll be able to use this command in "
                                                                      f"{cooldown} {time}")

        # Commands: DisabledCommand
        elif isinstance(error, commands.DisabledCommand):
            strs = [
                "That command has been disabled by the bot developers.",
                "It is likely unfinished or broken."
            ]

            return await self.notice_embeds.no_perms(ctx, "Command Disabled", '\n'.join(strs))

        # Commands: GuildDisabledCommand
        elif isinstance(error, errors.GuildDisabledCommand):
            return await self.notice_embeds.no_perms(ctx, f"Command Disabled",
                                                     "That command has been disabled in this server.")

        # Commands: NSFWChannelRequired
        elif isinstance(error, commands.NSFWChannelRequired):
            e = discord.Embed(
                title=":no_entry: Command is NSFW",
                color=discord.Color.red(),
                description="You can only use NSFW commands in NSFW channels."
            )

            e.set_image(url="https://i.imgur.com/oe4iK5i.gif")
            await ctx.reply(mention_author=False, embed=e)

        # Commands: NotOwner
        elif isinstance(error, commands.NotOwner):
            e = discord.Embed(
                title=":no_entry: Access Denied",
                description="Only bot developers and admins can use that command.",
                color=discord.Color.red()
            )

            e.set_image(url="https://cdn.discordapp.com/attachments/713675042143076356/843826600935555082/unknown.png")
            await ctx.reply(embed=e, mention_author=False)

        # Commands: NoPrivateMessage
        elif isinstance(error, commands.NoPrivateMessage):
            return await self.notice_embeds.error(ctx, "Command cannot be used in DMs",
                                                  "This command must be run in a guild.")

        # --------------------------------

        # Arguments: MissingRequiredArgument
        elif isinstance(error, commands.MissingRequiredArgument):
            lines = [
                f"`{ctx.prefix}{ctx.command} {ctx.command.usage if ctx.command.usage else ''}`",
                " ",
                str(ctx.command.help if ctx.command.help else ctx.command.brief)
            ]

            e = discord.Embed(
                title=f":question: How to use `{ctx.command}`",
                description='\n'.join(lines),
                color=discord.Color.green()
            )

            await self.help_utils.examples(ctx, ctx.command, e)
            # args = []
            # for arg in error.args:
            #     filtered_arg = arg.split()[0]
            #
            #     args.append(filtered_arg)
            #
            # if len(args) == 1:
            #     arg_count_notice = "is a required argument"
            #     title = "Argument"
            # else:
            #     arg_count_notice = "are required arguments"
            #     title = "Arguments"
            #
            # e = discord.Embed(
            #     title=f":x: Missing {title}",
            #     color=discord.Colour.red(),
            #     description=
            #     f"`{', '.join(args)}` {arg_count_notice} in this command."
            #     "\n⸻"
            # )
            #
            # e.add_field(name='Proper Usage', value=f"`{ctx.prefix}{ctx.command} {ctx.command.usage}`", inline=False)
            # await help.examples(ctx, e, ctx.command)
            # e.add_field(name='How to use', value=ctx.command.help, inline=False)
            # e.set_footer(text='<> - Required. [] - Optional')

            e.set_footer(text="<> - Required. [] - Optional")
            return await ctx.reply(mention_author=False, embed=e)

        # Arguments: BadBoolArgument
        elif isinstance(error, commands.BadBoolArgument):
            return await self.notice_embeds.error(ctx, "Bad Boolean Argument",
                                                  "Please check for spelling errors and try again.")

        # --------------------------------

        # Permissions: BotMissingPermissions
        elif isinstance(error, commands.BotMissingPermissions):
            p = str(error.missing_permissions[0]).replace("_", " ").title()

            return await self.notice_embeds.error(ctx, "Missing Permissions", f"I need the {p} permission to do that.")

        # Permissions: BotMissingPermissions
        elif isinstance(error, commands.MissingPermissions):
            p = str(error.missing_permissions[0]).replace("_", " ").title()

            return await self.notice_embeds.error(ctx, "Missing Permissions",
                                                  f"You need the {p} permission to do that.")

        # Permissions: ChannelNotReadable
        elif isinstance(error, commands.ChannelNotReadable):
            return await self.notice_embeds.error(ctx, "Channel Not Found", f"The bot cannot read `{error.argument}`.")

        # --------------------------------

        # 404: CommandNotFound
        elif isinstance(error, commands.CommandNotFound):
            suggestion = None
            title = "Command Does Not Exist"

            for command in self.client.all_commands:
                if self.client.all_commands[command].enabled and not self.client.all_commands[command].hidden:
                    ratio = round(SequenceMatcher(a=ctx.invoked_with, b=command).ratio(), 1)

                    if ratio >= 0.7:
                        suggestion = command

                        break

            if suggestion is None:
                return await self.notice_embeds.error(ctx, title, f"Use `{ctx.prefix}help` to see all my commands.")
            else:
                return await self.notice_embeds.error(ctx, title,
                                                      f"Perhaps you meant to run `{ctx.prefix}{suggestion}`?")

        # 404: MemberNotFound
        elif isinstance(error, commands.MemberNotFound):
            return await self.notice_embeds.error(ctx, "Member Not Found",
                                                  f"I couldn't find the member `{error.argument}` in this server.")

        # 404: ChannelNotFound
        elif isinstance(error, commands.ChannelNotFound):
            return await self.notice_embeds.error(ctx, "Channel Not Found", f"`{error.argument}` does not exist.")

        # 404: PartialEmojiConversionFailure
        elif isinstance(error, commands.PartialEmojiConversionFailure):
            return await self.notice_embeds.error(
                ctx, "Emoji Not Found", "That emoji does not exist or it is a default emoji."
            )

        # --------------------------------

        # General: RegularException
        elif isinstance(error, commands.CommandInvokeError):
            if isinstance(error, tuple(blocked)):
                return
            # Developer Log
            channel = self.client.get_channel(826727094205415464)

            # Trace data handling
            with open("error.txt", "w") as f:
                if len(''.join(format_exception(type(error), error, error.__traceback__))) > 2040:
                    f.write(''.join(format_exception(type(error), error, error.__traceback__)))
                    trace = 'Traceback is too big! Added as TXT File.'
                else:
                    trace = discord.utils.escape_markdown(''.join(format_exception(type(error), error, error.__traceback__)))

            de = discord.Embed(
                title=":x: Command Raised Exception",
                color=discord.Color.red(),
                description=f"```py\n{trace}```"
            )

            de.set_footer(text=f"{error.__cause__.__class__.__name__} | Command: {ctx.command} | ID: {ctx.message.id}")

            if ctx.guild is not None:
                de.add_field(name="Guild", value=f"{ctx.guild.name} ({ctx.guild.id})", inline=False)
                de.add_field(name="Channel", value=f"<#{ctx.channel.id}> ({ctx.channel.id})", inline=False)

            de.add_field(name="User", value=f"<@{ctx.author.id}> ({ctx.author.id})", inline=False)

            with open("error.txt", "r") as f:
                if ''.join(format_exception(type(error), error, error.__traceback__)) in f.read():
                    await channel.send(embed=de, file=discord.File("error.txt"))
                else:
                    await channel.send(embed=de)

            if platform.system() == "Windows":
                os.system('del error.txt')
            else:
                os.system('rm error.txt')

            # User log
            path = format_exception(type(error), error, error.__traceback__)[2].lstrip()
            ue = discord.Embed(
                title=f":x: Command Raised Exception",
                color=discord.Color.red(),
                description=f"```py\n{error.__cause__ if error.__cause__ else error}```"
            )

            ue.add_field(name="Where it happened", value=f"```py\n{discord.utils.escape_markdown(path)}```")
            ue.add_field(
                name="What to do next",
                value="Join the [support server](https://discord.gg/tuCpWgn5W8/)"
                      " and send this embed to <#827784007025557534>."
                      " In the meantime, try running the command again.",
                inline=False
            )
            ue.set_footer(text=f"{error.__cause__.__class__.__name__} | ID: {ctx.message.id}")

            # Command Locking
            if ctx.command.parent and ctx.command.parent.name == "dev":
                pass
                  
            try:
                await ctx.reply(embed=ue, mention_author=False)
            except discord.NotFound:
                await ctx.send(embed=ue)

            with open(f"{self.client.json}/blocked.json") as bjson:
                bdata = json.load(bjson)

            if ctx.command.name in bdata['commands'].keys():
                bdata['commands'][str(ctx.command.name)] += 1

                if bdata['commands'][str(ctx.command.name)] >= 10:
                    ctx.command.enabled = False
            else:
                bdata['commands'][str(ctx.command.name)] = 1

            with open(f"{self.client.json}/blocked.json", "w") as bjson:
                json.dump(bdata, bjson, indent=4)

        # General: IgnoredExceptions
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=stderr)
            print(format_exception(type(error), error, error.__traceback__))


def setup(client):
    client.add_cog(Events(client))
