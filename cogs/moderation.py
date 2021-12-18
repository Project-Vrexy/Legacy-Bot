# StdLib
import asyncio
from random import choice
import sqlite3
from datetime import datetime, timedelta

# Discord
import aiosqlite
import nextcord as discord
from nextcord.ext import commands
from dislash import Button, ButtonStyle, ActionRow

# Local Code
from cogs.utils.embeds import NoticeEmbeds
from cogs.utils.path import path

# Paths
p = path()

# Connections
con = sqlite3.connect(p + "/data/db/database.sqlite3")
cur = con.cursor()


# noinspection PyBroadException
class Moderation(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.emoji = '🛡️'
        self.desc = 'Commands that can help protect your server'
        self.not_everyone = True

        self.extras = {
            'purge': {
                'guild_only': True,
                'examples': {
                    "PlaceDet 10",
                    "\nPlaceDet 10 @Superchupu"
                }
            },
            'ban': {
                'guild_only': True,
                'examples': {
                    "PlaceDet @Superchupu G Spy"
                }
            },
            'kick': {
                'guild_only': True,
                'examples': {
                    "PlaceDet @Superchupu Stop"
                }
            },
            'unban': {
                'guild_only': True,
                'examples': {
                    "PlaceDet @Superchupu No longer G Spy"
                }
            },
            'tempban': {
                'guild_only': True,
                'examples': {
                    "PlaceDet @Superchupu 7d G Spy"
                }
            },
            'nuke': {
                'guild_only': True
            },
            'lock': {
                'guild_only': True
            },
            'unlock': {
                'guild_only': True
            }    
        }

        self.notice_embeds = NoticeEmbeds(client)

    # Purge
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.command(aliases=['clear', 'massdelete'], brief="Delete a certain amount of messages.",
                      usage="<amount> [member]")
    async def purge(self, ctx, limit: int, user: discord.Member = None):
        load = await self.notice_embeds.load(ctx, f"Deleting {limit} messages")
        await asyncio.sleep(2.5)
        await load.delete()

        if user is None:
            await ctx.channel.purge(limit=limit)
            delete_notice = f"Deleted {limit} messages."
        else:
            await ctx.channel.purge(limit=limit, check=lambda messages: messages.author.id == user.id)
            delete_notice = f"Deleted {limit} messages by {user}."

        e = discord.Embed(
            title=":white_check_mark: Done",
            description=delete_notice,
            color=discord.Color.green()
        )

        notice = await ctx.send(embed=e)
        await asyncio.sleep(2.5)
        await notice.delete()

    # Ban: Ban
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(brief="Ban a user from the server.", usage="<member> [reason]")
    async def ban(self, ctx, user: discord.Member, *, reason=None):
        if reason is None:
            reason = f"Auto-Ban by Aeon on behalf of {ctx.author}"
        e = discord.Embed(
            title=":shield: Banned!",
            description=f"You have been banned from `{ctx.guild.name}`!",
            color=discord.Colour.green()
        )

        e.add_field(name='Guild', value=ctx.guild.name, inline=False)
        e.add_field(name='Mod', value=ctx.author, inline=False)
        e.add_field(name='Reason', value=reason, inline=False)

        if user.top_role >= ctx.guild.me.top_role:
            await self.notice_embeds.error(ctx, "Error Banning", "The user has a higher/equal role than the bot!")
        else:
            nl = "\n"
            e = discord.Embed(
                title=f":white_check_mark: User banned",
                color=discord.Color.green(),
                description=f"{user.mention} has been banned {f'because: `%s %s`' % (reason, nl) if reason else '.'}"
            )
            await ctx.reply(embed=e)
            try:
                await user.send(embed=e)
            except discord.HTTPException:
                pass

            await ctx.guild.ban(user, delete_message_days=0, reason=reason)

    # Kick: Kick
    @commands.guild_only()
    @commands.has_permissions(kick_members=True)
    @commands.command(brief="Kick a user from the server.", usage="<member> [reason]")
    async def kick(self, ctx, user: discord.Member, *, reason=None):
        if reason is None:
            reason = f"Auto-Kick by Aeon on behalf of {ctx.author}"
        e = discord.Embed(
            title=":shield: Kicked!",
            description=f"You have been kicked from `{ctx.guild.name}`!",
            color=discord.Colour.green()
        )

        e.add_field(name='Guild', value=ctx.guild.name, inline=False)
        e.add_field(name='Mod', value=ctx.author, inline=False)
        e.add_field(name='Reason', value=reason, inline=False)

        if user.top_role >= ctx.guild.me.top_role:
            await self.notice_embeds.error(ctx, "Error Kicking", "The user has a higher/equal role than the bot!")
        else:
            nl = "\n"
            e = discord.Embed(
                title=f":white_check_mark: User Kicked",
                color=discord.Color.green(),
                description=f"{user.mention} has been kicked {f'because: `%s %s`' % (reason, nl) if reason else '.'}"
            )
            await ctx.reply(embed=e)
            try:
                await user.send(embed=e)
            except discord.HTTPException:
                pass

            await ctx.guild.kick(user, reason=reason)

    # Ban: Unban
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(brief="Unban a user from the server.", usage="<member> [reason]")
    async def unban(self, ctx, user: discord.User, *, reason=None):
        if reason is None:
            reason = f"Auto-Unban by Aeon on behalf of {ctx.author}"
        if user in ctx.guild.members:
            await self.notice_embeds.error(ctx, "Error Unbanning", "That user is already here!")
        elif user in await ctx.guild.bans():
            await self.notice_embeds.error(ctx, "Error Unbanning", "That user is not banned!")
        else:
            nl = "\n"
            e = discord.Embed(
                title=f":white_check_mark: User Unbanned",
                color=discord.Color.green(),
                description=f"{user.mention} has been unbanned {f'because: `%s %s`' % (reason, nl) if reason else '.'}"
            )
            await ctx.reply(embed=e)
            await ctx.guild.unban(user, reason=reason)

    # Ban: TempBan
    @commands.guild_only()
    @commands.has_permissions(ban_members=True)
    @commands.command(brief="Temporarily ban a user from the server.", usage="<user> <time> [reason]", enabled=False)
    async def tempban(self, ctx, user: discord.Member, _time, *, reason=None):
        if reason is None:
            reason = f"Auto-Unban by Aeon on behalf of {ctx.author}"
        nl = "\n"
        e = discord.Embed(
            title=":shield: Banned!",
            description=f"You have been banned from `{ctx.guild.name}` "
                        f"{f'because: `%s %s`' % (reason, nl) if reason else '.'}!",
            color=discord.Colour.green()
        )

        e.add_field(name='Guild', value=ctx.guild.name, inline=False)
        e.add_field(name='Mod', value=ctx.author, inline=False)
        e.add_field(name='Reason', value=reason, inline=False)

        if user.top_role >= ctx.guild.me.top_role:
            await self.notice_embeds.error(ctx, "Error Banning", "The user has a higher/equal role than the bot!")
        else:
            due = _time.split(" ")
            dict_timedelta = {}

            for format_ in due:
                if format_.lower().endswith("m"):
                    dict_timedelta["minutes"] = abs(int(format_.lower().replace("m", "")))

                if format_.lower().endswith("h"):
                    dict_timedelta["hours"] = abs(int(format_.lower().replace("h", "")))

                if format_.lower().endswith("d"):
                    dict_timedelta["days"] = abs(int(format_.lower().replace("d", "")))

                if format_.lower().endswith("w"):
                    dict_timedelta["weeks"] = abs(int(format_.lower().replace("w", "")))

            new_time = datetime.now() + timedelta(**dict_timedelta)

            nl = "\n"
            e = discord.Embed(
                title=f":white_check_mark: User banned",
                color=discord.Color.green(),
                description=f"{user.mention} has been banned for {_time} "
                            f"{f'because: `%s %s`' % (reason, nl) if reason else '.'}"
            )
            await ctx.reply(embed=e)
            try:
                await user.send(embed=e)
            except discord.HTTPException:
                pass

            async with await aiosqlite.connect(self.client.db) as db:
                await db.execute("INSERT INTO tempbans VALUES(:guild, :mod, :user, :time)", {
                    'guild': ctx.guild.id,
                    'mod': ctx.author.id,
                    'user': user.id,
                    'time': str(datetime.strftime(new_time, '%Y-%m-%d %H:%M:%S'))
                })

                await ctx.guild.ban(user, delete_message_days=0, reason=reason)
                await db.commit()

    # Nuke
    @commands.guild_only()
    @commands.has_permissions(manage_messages=True)
    @commands.command(brief="Nuke the channel. This is a very dangerous command.")
    async def nuke(self, ctx):
        buttons = ActionRow(Button(style=ButtonStyle.green, custom_id="yes", label="Yes"),
                            Button(style=ButtonStyle.red, custom_id="no", label="No"))

        e = discord.Embed(
            title=":warning: Nuke warning",
            color=discord.Color.green(),
            description="Are you you sure to nuke this channel?"
            "\n**Everything in this channel will be deleted.**"
        )

        msg = await ctx.reply(mention_author=False, embed=e, components=[buttons])
        events = msg.create_click_listener(timeout=30)

        @events.matching_id("yes")
        async def exec_nuke(inter):
            so = [
                "y doe",
                "boom :radioactive:",
                ":wastebasket: bshoop",
                ":cloud_tornado: AHHHHHHHHHHHHHHHHHH"
            ]

            # Why?
            ee = discord.Embed(
                title=choice(so),
                color=discord.Color.green()
            )

            await inter.reply(type=7, embed=ee, components=[])

            # Actual Nuking: Vars
            clone = await ctx.channel.clone()
            order = ctx.channel.position

            # Actual Nuking: NukeTime
            await ctx.channel.delete()
            await clone.edit(position=order)

            # Notice
            notice = await clone.send(f"<@{ctx.message.author.id}>, Done. :smile:")
            await asyncio.sleep(5)
            await notice.delete()
            events.kill()

        @events.matching_id("no")
        async def abort_nuke(inter):
            ea = discord.Embed(
                title="Ok, not doing that then",
                color=discord.Color.green(),
            )

            await inter.reply(type=7, embed=ea, components=[])
            events.kill()

        @events.timeout
        async def timeout_nuke():
            ea = discord.Embed(
                title="Ok, not doing that then",
                color=discord.Color.green(),
            )

            await msg.edit(embed=ea, components=[])

    @commands.command(brief="Lock a channel in the server.")
    async def lock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
            e = discord.Embed(
                title=":lock: Channel Locked",
                color=discord.Color.green(),
                description=f"{ctx.channel.mention} has been locked.\n"
                            "Regular members won't be able to send messages there anymore."
            )
        else:
            await channel.set_permissions(ctx.guild.default_role, send_messages=False)
            e = discord.Embed(
                title=":lock: Channel Locked",
                color=discord.Color.green(),
                description=f"{channel.mention} has been locked.\n"
                            "Regular members won't be able to send messages there anymore."
            )
        await ctx.send(embed=e)

    @commands.command(brief="Unlock a locked channel in the server.")
    async def unlock(self, ctx, channel: discord.TextChannel = None):
        if channel is None:
            await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
            e = discord.Embed(
                title=":unlock: Channel Unlocked",
                color=discord.Color.green(),
                description=f"{ctx.channel.mention} has been unlocked.\n"
                            "Regular members are now able to send messages there."
            )
        else:
            await channel.set_permissions(ctx.guild.default_role, send_messages=True)
            e = discord.Embed(
                title=":unlock: Channel Unlocked",
                color=discord.Color.green(),
                description=f"{channel.mention} has been unlocked."
                            "Regular members are now able to send messages there."
            )
        await ctx.send(embed=e)


def setup(client):
    client.add_cog(Moderation(client))
