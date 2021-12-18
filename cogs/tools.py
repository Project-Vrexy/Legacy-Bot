# StdLib
import os
import platform
import random
import re
import base64
import sqlite3
from time import time
from asyncio import sleep
from datetime import datetime, timedelta

# Discord
import nextcord as discord
from nextcord.ext import commands
from nextcord import Embed

# Third Party
import matplotlib.pyplot as plt
import ujson as json
import aiosqlite
import requests
import ocrspace
from googletrans import Translator
from pandas import read_json
from pytz import utc
from aiohttp import ClientSession
from currency_symbols import CurrencySymbols
from difflib import SequenceMatcher
from dislash import Button, ButtonStyle, ActionRow
from PIL import Image, ImageDraw, ImageFont, ImageColor


# Local Code
from cogs.utils.help import HelpUtils, HelpMenus
from cogs.utils.embeds import NoticeEmbeds, EmbedUtils
from cogs.utils.custom_checks import WaitForChecks
from cogs.utils.paginator import Paginator
from cogs.utils.path import path

# Paths
p = path()

con = sqlite3.connect(p + '/data/db/database.sqlite3')
cur = con.cursor()


# noinspection PyBroadException
class Tools(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.translator = Translator()
        
        self.emoji = '🔨'
        self.desc = 'Commands that can do a variety of things'

        self.extras = {
            'remind': {
                'create': {
                    'examples': {
                        "PlaceDet 5m Post H"
                    }
                }
            },
            'tags': {
                'emoji': ':label:',
                'guild_only': True,
                'create': {
                    'examples': [
                        f"PlaceDet turkey"
                    ]
                }
            },
            'suggest': {
                'guild_only': True
            },
            'snipe': {
                'guild_only': True
            },
        }

        self.embed_utils = EmbedUtils(client)
        self.notice_embeds = NoticeEmbeds(client)
        self.help_utils = HelpUtils(client)
        self.helpmenus = HelpMenus(client)

        self.abr = "To abort, type `abort`."
        self.abr2 = "User requested abort."

        self.alias_guild = 862743663151153192

    # Reminders: Group
    @commands.group(brief="Remind yourself of something at a later time.", aliases=["remindme", "reminders"])
    async def remind(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.helpmenus.menu(
                context=ctx, group_get='remind',
                title=":bell: Reminders",
                description="List, add, remove and view reminders using these commands!"
            )

    # Reminders: List
    @remind.command(brief="List all reminders you've made.", aliases=["list"])
    async def show(self, ctx):
        with con:
            reminders = []
            cur.execute("SELECT * FROM reminders WHERE user_id = :author", {
                'author': ctx.author.id
            })

            records = cur.fetchall()

            for row in records:
                if len(row[2]) >= 35:
                    split = [row[2][i:i + 35] for i in range(0, len(row[2]), 35)]
                    drt = f"{split[0]}..."
                else:
                    drt = row[2]

                reminders.append(f"• `{row[0]}` - `{drt}`")

            desc = '\n'.join(reminders) if reminders else "You have no reminders added!"
            e = discord.Embed(
                title=":bell: Reminders",
                color=discord.Color.green(),
                description=desc
            )

            await ctx.reply(mention_author=False, embed=e)

    # Reminders: Add
    @remind.command(usage="<#m/h/d/w/m/y> <text>", brief="Add a reminder.", aliases=["create"])
    async def add(self, ctx, _time, *, reminder):
        due = _time.split(" ")
        dict_timedelta = {}

        def end(_str):
            return format_.lower().endswith(_str)

        for format_ in due:
            if format_.lower().endswith("s"):
                return await self.notice_embeds.error(ctx, 'Error Creating Reminder',
                                                      'Reminders only support minutes, hours, days and weeks as '
                                                      'numbers.')

            if format_.lower().endswith("m"):
                try:
                    dict_timedelta["minutes"] = abs(int(format_.lower().replace("m", "")))
                except ValueError:
                    return await self.notice_embeds.error(ctx, 'Error Creating Reminder',
                                                          'Reminders only support minutes, hours, days and weeks as '
                                                          'numbers.')

            if format_.lower().endswith("h"):
                try:
                    dict_timedelta["hours"] = abs(int(format_.lower().replace("h", "")))
                except ValueError:
                    return await self.notice_embeds.error(ctx, 'Error Creating Reminder',
                                                          'Reminders only support minutes, hours, days and weeks as '
                                                          'numbers.')

            if format_.lower().endswith("d"):
                try:
                    dict_timedelta["days"] = abs(int(format_.lower().replace("d", "")))
                except ValueError:
                    return await self.notice_embeds.error(ctx, 'Error Creating Reminder',
                                                          'Reminders only support minutes, hours, days and weeks as '
                                                          'numbers.')

            if format_.lower().endswith("w"):
                try:
                    dict_timedelta["weeks"] = abs(int(format_.lower().replace("w", "")))
                except ValueError:
                    return await self.notice_embeds.error(ctx, 'Error Creating Reminder',
                                                          'Reminders only support minutes, hours, days and weeks as '
                                                          'numbers.')

            if not end("m") and not end("h") and not end("d") and not end("w"):
                return await self.notice_embeds.error(ctx, 'Error Creating Reminder',
                                                      'Reminders only support minutes, hours, days and weeks as '
                                                      'numbers.')

        new_time = datetime.now() + timedelta(**dict_timedelta)

        with con:
            cur.execute("SELECT * FROM reminders WHERE user_id = :author", {
                'author': ctx.author.id
            })

            reminders = cur.fetchall()

            if len(reminders) > 10:
                return await self.notice_embeds.error(ctx, "Error Creating Reminder",
                                                      "You can only have up to 10 reminders at a time")

            cur.execute("INSERT INTO reminders VALUES (NULL, :author, :reminder, :time)", {
                'author': ctx.author.id,
                'reminder': reminder,
                'time': str(datetime.strftime(new_time, '%Y-%m-%d %H:%M:%S'))
            })

            cur.execute("SELECT * FROM reminders WHERE reminder = :reminder AND user_id = :author", {
                'reminder': reminder,
                'author': ctx.author.id
            })

            reminder = cur.fetchall()

            for row in reminder:
                row_id = row[0]

            e = discord.Embed(
                title=f":bell: {random.choice(['Awesome!', 'Nice!', 'Cool!', 'Sick!'])}",
                color=discord.Color.green(),
                description=f"You will be reminded in {_time}"
            )

            e.set_footer(text=f"Reminder ID: {row_id}")

            await ctx.reply(embed=e, mention_author=False)

    # Reminders: Remove
    @remind.command(usage="<id>", brief="Delete a reminder.", description="31", aliases=["delete"])
    async def remove(self, ctx, _id):
        with con:
            cur.execute("SELECT * FROM reminders WHERE id = :i AND user_id = :a", {'i': _id, 'a': ctx.author.id})
            records = cur.fetchall()

            if len(records) == 0:
                return await self.notice_embeds.error(ctx, "Error Deleting Reminder", "You do not have a reminder "
                                                                                      "with that ID.")

            cur.execute("DELETE FROM reminders WHERE id = :id", {'id': _id})
            e = Embed(title=":bell: Reminders", color=discord.Color.green(), description=f"Deleted reminder {_id}!")

            await ctx.reply(mention_author=False, embed=e)

    # Reminders: View
    @remind.command(usage="<id>", brief="View a reminder.", description="31")
    async def view(self, ctx, _id):
        with con:
            cur.execute("SELECT * FROM reminders WHERE id = :i AND user_id = :a", {'i': _id, 'a': ctx.author.id})
            reminder = cur.fetchone()

            if reminder is None:
                return await ctx.reply("You have no reminder with that ID!")

            e = discord.Embed(
                title=":bell: Viewing reminder",
                color=discord.Color.green(),
                description=reminder[2],
                timestamp=datetime.strptime(reminder[3][:-7], '%Y-%m-%d %H:%M:%S').astimezone(utc)
            )

            e.set_footer(text="Due:")
            e.add_field(name="ID", value=reminder[2])
            await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Tags: Group
    @commands.guild_only()
    @commands.group(
        brief="Allow you to tag text for later retrieval.", aliases=["t", "tag"], invoke_without_command=True
    )
    async def tags(self, ctx, *, name=None):
        if ctx.invoked_subcommand is not None:
            return

        if name is None:
            return await self.helpmenus.paginated_menu(
                context=ctx,
                group_get='tags',
                title=":label: Tags",
                description='\n'.join([
                    "Allow you to tag text for later retrieval.",
                    "If a subcommand is not passed, it will fetch a tag."
                ]),
                split_per_page=3
            )

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT * FROM tags WHERE guild_id = :guild", {'guild': ctx.guild.id}) as \
                    cursor:
                records = await cursor.fetchall()
                tags = [row[3] for row in records]

            async with await db.execute("SELECT * FROM tags WHERE name = :tag AND guild_id = :guild", {
                'tag': name,
                'guild': ctx.guild.id
            }) as cursor:
                tag = await cursor.fetchone()

            if tag is None:
                suggested = None

                for added_tag in tags:
                    ratio = round(SequenceMatcher(a=name, b=added_tag).ratio(), 1)

                    if ratio >= 0.7:
                        suggested = added_tag
                        break

                error = "That tag does not exist" if suggested is None else f"That tag does not exist. Perhaps you " \
                                                                            f"meant `{suggested}`? "
                return await self.notice_embeds.error(ctx, "Error Getting Tag", error)

            e = discord.Embed(
                title=f":label: {tag[3]}",
                description=tag[4],
                color=discord.Color.green()
            )

            await ctx.reply(embed=e, mention_author=False)

            await db.execute("UPDATE tags SET uses = :u WHERE guild_id = :g AND name = :n",
                             {'u': tag[6] + 1, 'g': ctx.guild.id, 'n': name})
            await db.commit()

    # Tags: Create
    @tags.command(brief="Create tags for later retrieval of text.", usage="<name>", description="turkey")
    async def create(self, ctx, *, name):
        fc = []
        g = self.client.get_command(name='tags')

        for command in g.commands:
            fc.append(command.name)
            fc.extend(command.aliases)

        if name.lower().split(" ")[0] in fc:
            return await self.notice_embeds.error(ctx, "Error Creating Tag", "That tag name starts with a reserved "
                                                                             "word.")
        if len(name) > 25:
            return await self.notice_embeds.error(ctx, "Error Creating Tag", "Tag names can only be 25 characters or "
                                                                             "shorter.")
        elif "```" in name:
            return await self.notice_embeds.error(ctx, "Error Creating Tag", "`Backtick` is an invalid character in "
                                                                             "tag names.")

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT * FROM tags WHERE name = :n AND guild_id = :g",
                                        {'n': name, 'g': ctx.guild.id}) as cursor:
                tag = await cursor.fetchone()

                if tag:
                    return await self.notice_embeds.error(ctx, "Error Creating Tag", "That tag already exists.")

            async with await db.execute("SELECT * FROM tags WHERE guild_id = :guild", {'guild': ctx.guild.id}) as \
                    cursor:
                tags = await cursor.fetchall()

                if len(tags) >= 250:
                    return await self.notice_embeds.error(ctx, "Error Creating Tag",
                                                          "Your server has run out of tags. (250)")

            e = discord.Embed(title=":label: What should the content of this tag be?", color=discord.Color.green(),
                              description=self.abr)

            em = await ctx.reply(mention_author=False, embed=e)
            waitcheck = WaitForChecks(self.client, ctx)
            c = await self.client.wait_for('message', check=waitcheck.aligned_ctx)

            if c.content.lower() != "abort":
                await db.execute(
                    "INSERT INTO tags VALUES (NULL, :g, :u, :n, :c, :t, :us)",
                    {
                        'g': ctx.guild.id,
                        'u': ctx.author.id,
                        'n': str(name),
                        'c': c.content,
                        't': str(datetime.now())[:-7],
                        'us': str('0')
                    }
                )

                await db.commit()
                e = discord.Embed(title=":label: Tag Created", color=discord.Color.green(),
                                  description=f"Created tag `{name}`")
            else:
                e = discord.Embed(title=":label: Tag Creation Aborted", color=discord.Color.green(),
                                  description="User requested abort")

            await em.edit(embed=e)

    # Tags: Edit
    @tags.command(brief="Edit the text within a tag.", usage="<name>", description="kurdish")
    async def edit(self, ctx, *, name):
        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute(
                    "SELECT * FROM tags WHERE name = :name AND guild_id = :guild_id AND user_id = :user_id",
                    {'name': name, 'guild_id': ctx.guild.id, 'user_id': ctx.author.id}
            ) as cursor:
                tag = await cursor.fetchone()

            if tag is None:
                return await self.notice_embeds.error(ctx, "Error Editing Tag",
                                                      "That tag does not exist or you do not own it.")

            e = Embed(title=":label: What should the edited content of this tag be?", color=discord.Color.green(),
                      description=self.abr)

            em = await ctx.reply(mention_author=False, embed=e)
            waitcheck = WaitForChecks(self.client, ctx)

            c = await self.client.wait_for(
                'message',
                check=waitcheck.aligned_ctx
            )

            if c.content.lower() == 'abort':
                e = discord.Embed(
                    title=":label: Tag Edit Aborted",
                    color=discord.Color.green(),
                    description="User requested abort"
                )

                return await em.edit(embed=e)

            await db.execute(
                "UPDATE tags SET text = :text WHERE name = :name and guild_id = :guild_id",
                {'name': name, 'text': c.content, 'guild_id': ctx.guild.id}
            )

            e = Embed(
                title=":label: Tag Edited",
                color=discord.Color.green(),
                description=f"Edited tag `{name}`"
            )

            await em.edit(embed=e)
            await db.commit()

    # Tags: Claim
    @tags.command(brief="Claim the tags of a user not in the guild.", usage="<tag>", description="funny",
                  aliases=["takeown"])
    async def claim(self, ctx, *, name):
        async with aiosqlite.connect(self.client.db) as db:
            async with db.execute("SELECT * FROM tags WHERE name = :name AND guild_id = :guild", {
                'name': name,
                'guild': ctx.guild.id
            }) as cursor:
                tag = await cursor.fetchone()

            if tag is None:
                return await self.notice_embeds.error(ctx, "Error Claiming Tag", "That tag doesn't exist.")

            user = self.client.get_user(tag[2])

            if user in ctx.guild.members:
                return await self.notice_embeds.error(ctx, "Error Claiming Tag",
                                                      "The tag's owner is still in the guild.")

            await db.execute("UPDATE tags SET user_id = :a WHERE name = :n AND guild_id = :g", {
                'a': ctx.author.id, 'n': tag, 'g': ctx.guild.id
            })

            e = discord.Embed(title=":label: Claimed Tag", color=discord.Color.green(),
                              description=f"Claimed tag `{tag}`")
            await ctx.reply(mention_author=False, embed=e)
            await db.commit()

    # Tags: Aliases
    @tags.command(name="aliases", brief="Create an alias to a tag.", usage="<tag>")
    async def _alias(self, ctx, name):
        pass

    # Tags: Delete
    @tags.command(brief="Delete a tag.", usage="<name>", description="neutronrank", aliases=["remove"])
    async def delete(self, ctx, *, name):
        buttons = ActionRow(
            Button(style=ButtonStyle.green, label="Yes", custom_id="Nuke.Confirm.True"), Button(style=ButtonStyle.red,
                                                                                                label="No"))

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT * FROM tags WHERE name = :name AND guild_id = :guild AND user_id = "
                                        ":author", {
                                            'name': name,
                                            'guild': ctx.guild.id,
                                            'author': ctx.author.id
                                        }) as cursor:
                tag = await cursor.fetchone()

            if tag is None:
                return await self.notice_embeds.error(ctx, "Error Deleting Tag",
                                                      "That tag does not exist or you do not own it.")

            e = discord.Embed(
                title=":warning: Are you sure you want to delete this tag?",
                color=discord.Color.gold(),
                description="This action cannot be undone."
            )

            em = await ctx.reply(mention_author=False, embed=e, components=buttons)
            events = em.create_click_listener(timeout=15)

            @events.matching_id("Nuke.Confirm.True")
            async def confirm(inter):
                async with aiosqlite.connect(self.client.db) as dbi:
                    await dbi.execute("DELETE FROM tags WHERE name = :name AND guild_id = :guild", {
                        'name': name,
                        'guild': ctx.guild.id
                    })
                    e2 = discord.Embed(
                        title=":label: Tag Deleted",
                        color=discord.Color.green(),
                        description=f"Deleted tag `{name}`"
                    )
                    await inter.respond(type=7, embed=e2, components=[])
                    await dbi.commit()
                    events.kill()

            @events.matching_id("Nuke.Confirm.False")
            async def ignore(inter):
                e2 = discord.Embed(
                    title=":label: Ok, then.",
                    color=discord.Color.green(),
                    description=f"`{name}` was not deleted."
                )
                await inter.respond(type=7, embed=e2, components=[])
                events.kill()

            @events.timeout
            async def timeout():
                e2 = discord.Embed(
                    title=":label: Tag Deletion Aborted",
                    color=discord.Color.green(),
                    description="15 seconds have passed."
                )
                return await em.edit(embed=e2, components=[])

    # Tags: View
    @tags.command(brief="View info on a a tag.", usage="<name>", description="meon")
    async def view(self, ctx, *, name):
        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT * FROM tags WHERE name = :name AND guild_id = :guild", {
                'name': name,
                'guild': ctx.guild.id
            }) as cursor:
                tag = await cursor.fetchone()

            if tag is None:
                return await self.notice_embeds.error(ctx, "Error Viewing Tag", "That tag does not exist.")

            e = discord.Embed(
                title=":label: Tag Info",
                color=discord.Color.green()
            )

            e.add_field(name="Name", value=tag[3], inline=False)
            e.add_field(name="Created By", value=f"<@{tag[2]}>", inline=False)
            e.add_field(name="Created At", value=str(datetime.strptime(tag[5], '%Y-%m-%d %H:%M:%S')), inline=False)
            e.add_field(name="Uses", value=f"{str(tag[6])} uses.")

            await ctx.reply(mention_author=False, embed=e)

    # Tags: List
    @tags.command(name="list", brief="List all tags in your server.", usage=" ", description=" ")
    async def _list(self, ctx):
        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT * FROM tags WHERE guild_id = :guild", {
                'guild': ctx.guild.id
            }) as cursor:
                records = await cursor.fetchall()

        tags = [row[3] for row in records]
        pages = []

        if not tags:
            return await self.notice_embeds.error(ctx, "Error Listing Tags",
                                                  "This server does not have tags to list.")

        tags.sort()
        split_tags = await self.help_utils.page_split(_list=tags, split=25)

        for i in range(len(split_tags)):
            tag_page = split_tags[i]
            e = discord.Embed(
                title=":label: Tags List",
                color=discord.Color.green(),
                description=f"```yaml\n{', '.join(tag_page)}```"
            )

            e.set_footer(
                text=f"Viewing page {i + 1}/{len(split_tags)} • {len(tag_page)}/{len(tags)} displayed  • "
                     f"{len(tags)}/250 tags used "
            )

            # await ctx.send(embed=e)
            pages.append(e)

        paginator = Paginator(self.client, ctx, pages)
        await paginator.run()

    # --------------------------------

    # Suggestions: Group
    @commands.guild_only()
    @commands.group(brief="Suggest something, that's it.")
    async def suggest(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.helpmenus.menu(
                context=ctx, group_get='suggest',
                title=':bulb: Suggestions',
                description="Use this to suggest something. That's it, no more, no less."
            )

    # Suggestions: Create
    @suggest.command(name="create", usage="<suggestion>")
    async def _create(self, ctx, *, suggestion=None):
        if suggestion is None:
            return await self.notice_embeds.error(ctx, 'Error Suggesting', 'You need to provide a suggestion.')

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute(
                    'SELECT suggestions FROM config WHERE id = :id',
                    {'id': ctx.guild.id}
            ) as cursor:
                config = await cursor.fetchone()

            if None in config:
                strs = [
                    'This server has not been setup for suggestions.',
                    f'**For Guild Admins:** Set it up using `{ctx.prefix}suggest channel <channel>`.'
                ]

                return await self.notice_embeds.error(ctx, 'Error Suggesting', '\n'.join(strs))

            # Channel Embed
            e = discord.Embed(
                description=suggestion,
                color=discord.Color.green(),
                timestamp=datetime.now().astimezone(utc)
            )

            url = "https://cdn.discordapp.com/attachments/713675042143076356/843488946796363816/unknown.png"

            e.set_author(name=f"{ctx.author.name} suggests...", icon_url=url)
            e.set_thumbnail(url=ctx.author.display_avatar.url)

            channel = await self.client.fetch_channel(config[0])
            message = await channel.send(embed=e)

            await message.add_reaction('✅')
            await message.add_reaction('❓')
            await message.add_reaction('❌')

            e.set_footer(text=f"Suggestion ID: {message.id}")
            await message.edit(embed=e)

            await db.execute('INSERT INTO suggestions VALUES (:id, :guild, :user, :suggestion, :time)', {
                'id': message.id,
                'guild': ctx.guild.id,
                'user': ctx.author.id,
                'suggestion': str(suggestion),
                'time': str(datetime.now().astimezone(utc).strftime('%Y-%m-%d %H:%M:%S'))
            })
            await db.commit()

            # User Embed
            e = discord.Embed(
                title=":white_check_mark: Success",
                description=f"That suggestion has been posted in <#{config[0]}>.",
                color=discord.Color.green()
            )

            e.set_footer(text=f"ID: {message.id}")
            await ctx.reply(embed=e, mention_author=None)

    # Suggestions: Delete
    @suggest.command(name="delete")
    async def _delete(self, ctx, message=None):
        if message is None:
            return await self.notice_embeds.error(ctx, 'Error Deleting Suggestion',
                                                  'You need to provide a suggestion ID.')

        try:
            message = abs(int(message))
        except ValueError:
            return await self.notice_embeds.error(ctx, 'Error Deleting Suggestion',
                                                  'You need to provide a suggestion ID.')

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute(
                    "SELECT * FROM suggestions WHERE id = :id AND guild = :guild AND user = :author", {
                        'id': message,
                        'author': ctx.author.id,
                        'guild': ctx.guild.id
                    }) as cursor:
                records = await cursor.fetchone()

            if records is None:
                return await self.notice_embeds.error(ctx, 'Error Deleting Suggestion',
                                                      'You don\'t have any suggestions with that ID.')

            async with await db.execute(
                    'SELECT suggestions FROM config WHERE id = :id',
                    {'id': ctx.guild.id}
            ) as cursor:
                config = await cursor.fetchone()

            if None in config:
                strs = [
                    'This server has not been setup for suggestions.',
                    f'**For Guild Admins:** Set it up using `{ctx.prefix}suggest channel <channel>`.'
                ]

                return await self.notice_embeds.error(ctx, 'Error Deleting Suggestion', '\n'.join(strs))

        channel = await self.client.fetch_channel(abs(int(config[0])))

        try:
            msg = await channel.fetch_message(message)
            await msg.delete()
        except commands.MessageNotFound:
            await self.notice_embeds.error(ctx, 'Error Deleting Suggestion',
                                           'I cannot delete that suggestion from the channel as it has been changed.')

        e = discord.Embed(
            title=":white_check_mark: Deleted Suggestion",
            description="That suggestion is now gone.",
            color=discord.Color.green()
        )
        await ctx.send(embed=e)

    # ------------------------------

    # Snipe
    @commands.guild_only()
    @commands.command(brief="Shows the last deleted message in a channel.")
    async def snipe(self, ctx):
        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT * FROM snipes WHERE channel_id = :id", {
                'id': ctx.channel.id
            }) as cursor:
                snipe = await cursor.fetchone()

            if snipe is None:
                return await self.notice_embeds.error(ctx, "Error Sniping", "There is nothing to snipe.")

            e = discord.Embed(
                color=discord.Color.green(),
                description=snipe[2],
                timestamp=datetime.strptime(snipe[3][:-7], '%Y-%m-%d %H:%M:%S').astimezone(utc)
            )

            user = self.client.get_user(snipe[1])

            e.set_author(name=f"{user.name} said...", icon_url=user.display_avatar.url)
            await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Country
    @commands.cooldown(1, 10, commands.BucketType.default)
    @commands.command(brief='Get info about a certain country.', usage='<country name/2-3 letter character code>',
                      help=f"`PlaceDetcountry us`" "\n `PlaceDetcountry poland`", enabled=False)
    async def country(self, ctx, country: str):
        load = await ctx.reply("<a:load:827975573443051570> Getting country data", mention_author=False)
        start = time()
        async with ClientSession() as session:
            fields = "name;latlng;capital;subregion;nativeName;demonym;alpha2Code;population"
            args = f"{country}?fullText=true&fields={fields}"

            uri = f"https://restcountries.eu/rest/v2/name/{args}"

            async with session.get(uri) as api:
                emoji = "https://cdn.discordapp.com/attachments/713675042143076356/836740831456526407/unknown.png"

                if api.status == 404:
                    await self.notice_embeds.load_error(load, "An Error Occurred", "This city does not exist.")
                elif api.status == 200:
                    data = await api.json()
                    d = data[0]

                    e = discord.Embed(
                        title=f":flag_{d['alpha2Code'].lower()}: {d['name']} ({d['alpha2Code']})",
                        color=discord.Color.green(),
                    )

                    e.add_field(name="Latitude/Longitude", value=f"{d['latlng'][0]}, {d['latlng'][1]}")
                    e.add_field(name="Capital", value=d['capital'])
                    e.add_field(name='Continent', value=d['subregion'])
                    e.add_field(name="Nationality", value=d['demonym'])
                    e.add_field(name="Native Name", value=d['nativeName'])
                    e.add_field(name="Population", value=d['population'])

                    e.set_author(name="Country Info", icon_url=emoji)

                    end = time()
                    final = round(end - start, 2)

                    e.set_footer(text=f"Via RestCountries | Fetched in {final}s")
                    await load.edit(content=None, embed=e, mention_author=False)
                else:
                    await self.notice_embeds.load_error(load, "An Error Occurred",
                                                        "The API is not available. Please try again later.")
                    e = discord.Embed(
                        title=":x: An Error Occurred",
                        color=discord.Colour.red(),
                        description="The API is currently not available. In the meantime, try again later."
                    )

                    await load.edit(content=None, embed=e, mention_author=False)

    # Weather
    @commands.cooldown(1, 15, commands.BucketType.default)
    @commands.command(brief='Get the weather from a certain area.', usage='<city>',
                      help="`PlaceDetweather london`" "\n `PlaceDetweather 31-310`")
    async def weather(self, ctx, *city: str):
        """
        Gets the weather in a specified area.
        """

        load = await self.notice_embeds.load(ctx=ctx, message="Getting Weather Data")
        start = time()

        async with ClientSession() as session:
            args = f"q={'%20'.join(city)}&appid=11e930fa3a2749aa89967a378e5ac46c&units=metric"
            uri = f"https://api.openweathermap.org/data/2.5/weather?{args}"

            async with session.get(uri) as api:
                wd = await api.json()

                if api.status == 404:
                    await self.notice_embeds.load_error(load, "An Error Occurred",
                                                        "This city is not supported by this API.")
                elif api.status == 200:
                    e = discord.Embed(
                        title=f":white_sun_cloud: Weather in {wd['name']} "
                              f"({wd['sys']['country']} :flag_{wd['sys']['country'].lower()}:)",
                        color=discord.Color.green(),
                    )

                    c = wd['coord']
                    w0 = wd['weather'][0]
                    m = wd['main']
                    w = wd['wind']

                    e.add_field(name='Coords', value=f"{c['lon']}, {c['lat']}")
                    e.add_field(name='Weather', value=w0['description'].title())
                    await self.embed_utils.spacer(embed=e)
                    e.add_field(name='Temperature', value=f"{int(m['temp'])} °C")
                    e.add_field(name='Feels Like', value=f"{int(m['feels_like'])} °C")
                    e.add_field(name='Low', value=f"{int(m['temp_min'])} °C")
                    e.add_field(name='High', value=f"{int(m['temp_max'])} °C")
                    await self.embed_utils.spacer(embed=e)
                    e.add_field(name='Pressure', value=f"{int(m['pressure'])} hPa")
                    e.add_field(name='Humidity', value=f"{int(wd['main']['humidity'])}%")
                    e.add_field(name='Wind', value=f"{w['speed']} km/h at {w['deg']}°")

                    end = time()
                    final = round(end - start, 2)

                    e.set_footer(text=f"Via OpenWeatherMap | Fetched in {final}s")
                    await load.edit(embed=e)
                else:
                    await self.notice_embeds.load_error(load, "An Error Occurred",
                                                        "The API is not available. Please try again later.")

    # Bitcoin
    @commands.command(brief='Get the current Bitcoin price.', aliases=['btc'],
                      usage="[currency]", description="TRY")
    @commands.cooldown(1, 5, commands.BucketType.default)
    async def bitcoin(self, ctx, currency: str = 'usd'):
        start = time()
        load = await self.notice_embeds.load(ctx=ctx, message="Getting Bitcoin Price")

        async with ClientSession() as session:
            uri = f"https://api.coindesk.com/v1/bpi/historical/close.json?currency={currency.upper()}"
            sym = CurrencySymbols.get_symbol(currency.upper())

            async with session.get(uri) as api:
                try:
                    js = await api.json(content_type=None)
                except Exception:
                    await self.notice_embeds.load_error(load, "An Error Occurred", "That is not a valid currency.")

                bitcoin = str(js).replace("'", '"')
                bj = json.loads(bitcoin)

                with open("bitcoin.json", "w") as f:
                    f.write(bitcoin)

                btc = read_json("bitcoin.json")

                plt.rcParams['text.color'] = 'white'
                plt.rcParams['axes.labelcolor'] = 'white'
                plt.rcParams['xtick.color'] = 'white'
                plt.rcParams['ytick.color'] = 'white'
                plt.rcParams['legend.facecolor'] = 'black'
                plt.rcParams['figure.edgecolor'] = (0.8, 0.8, 0.8)
                fig, axes = plt.subplots(nrows=1, ncols=1, figsize=(16, 4))
                axes.set_facecolor((0.125, 0.133, 0.145))
                [axes.spines[x].set_color((0.8, 0.8, 0.8)) for x in ["bottom", "top", "left", "right"]]
                fig.set_facecolor((0.125, 0.133, 0.145))
                try:
                    btc.plot(ax=axes, grid=True, xlabel="Date", ylabel=f"Price ({currency.upper()})",
                             color=(0.18, 0.8, 0.443))
                except IndexError:
                    raise ValueError("No valid data to graph")
                plt.savefig("bgraph.png")

                e = discord.Embed(
                    title=f":coin: Current Bitcoin Price",
                    description=f"Last updated on {str(datetime.fromisoformat(bj['time']['updatedISO']))[:-9]}",
                    color=discord.Colour.green()
                )

                e.add_field(name="Current Price", value=f"{round(list(bj['bpi'].values())[-1], 2)}{sym}")

                daily = round(round(list(bj['bpi'].values())[-2], 2) / round(list(bj['bpi'].values())[-1], 2), 2)
                e.add_field(
                    name="Daily Difference",
                    value=f"{int(100 - daily * 100)}%"
                )

                weekly = round(round(list(bj['bpi'].values())[-7], 2) / round(list(bj['bpi'].values())[-1], 2), 2)
                e.add_field(
                    name="Weekly Difference",
                    value=f"{int(100 - weekly * 100)}%"
                )
                e.set_image(url="attachment://bgraph.png")

                end = time()
                final = round(end - start, 2)

                e.set_footer(text=f"Via CoinDesk | Fetched in {final}s")
                await load.delete()
                await ctx.reply(embed=e, file=discord.File("bgraph.png"), mention_author=False)

                if platform.system() == "Windows":
                    os.system('del bgraph.png')
                    os.system('del bitcoin.json')
                else:
                    os.system('rm bgraph.png')
                    os.system('rm bitcoin.json')

    # --------------------------------

    # Poll
    @commands.command(brief="Creates a poll, it's in the name.",
                      usage="<question> <option 1> <option 2> [option 3]...[option 10]",
                      help="`PlaceDetpoll \"Which bot is better?\" Aeon Meon`"
                           "\n`PlaceDetpoll Lasagna? yes no`")
    async def poll(self, ctx, question, *options: str):
        """
        Creates a poll for users to vote on.

        If only two options are provided, which are `yes` and `no`, it will display a Yes or No poll.
        Otherwise, it will display with numbers to vote with
        """

        if len(options) <= 1:
            return await self.notice_embeds.error(ctx, "Failed to Create Poll",
                                                  "You need at least 2 options to make a poll.")
        if len(options) > 10:
            return await self.notice_embeds.error(ctx, "Failed to Create Poll",
                                                  "You need at most 10 options to make a poll.")

        tt = ('yes', 'y', 'true', 't', '1')
        ft = ('no', 'n', 'false', 'f', '0')

        if len(options) == 2 and options[0] in tt and options[1] in ft:
            reactions = ['✅', '❌']
        else:
            reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟']

        description = []
        for x, option in enumerate(options):
            description += f"\n{reactions[x]} {option}"
        e = discord.Embed(
            title=question,
            color=discord.Color.green(),
            description=''.join(description)
        )

        e.set_footer(text=ctx.author.name, icon_url=ctx.author.display_avatar.url)

        rm = await ctx.send(embed=e)
        for reaction in reactions[:len(options)]:
            await rm.add_reaction(reaction)

    # --------------------------------

    # Options
    @commands.command(brief="Picks a random option from the given list. Use `\"` to have sentences in choices.",
                      usage="<options>", description='"The Letter H" "The Letter G"', aliases=["pick"])
    async def options(self, ctx, *options):
        e = discord.Embed(
            title=":crystal_ball: The Magic Orb",
            color=discord.Color.green(),
            description=f"**It picked:** {random.choice(options)}"
        )

        await ctx.reply(mention_author=False, embed=e)

    # Dice
    @commands.command(brief="Roll a dice.", aliases=["roll"])
    async def dice(self, ctx):
        load = await ctx.reply(":game_die: Rolling...")
        await sleep(2.5)

        dice = random.randint(1, 6)

        e = discord.Embed(
            title=":game_die: Dice Rolled",
            color=discord.Color.green(),
            description=f"**You Got:** {dice}"
        )

        await load.delete()
        await ctx.reply(mention_author=False, embed=e)

    # Coin
    @commands.command(brief="Flip a coin.", aliases=["flip"])
    async def coin(self, ctx):
        load = await ctx.reply(":coin: Flipping..")
        await sleep(2.5)

        options = ["Head", "Tails"]

        e = discord.Embed(
            title=":coin: Coin Flipped",
            color=discord.Color.green(),
            description=f"**You Got:** {random.choice(options)}"
        )

        await load.delete()
        await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Calculate
    @commands.command(
        brief="Calculates the given calculation, duh.",
        usage="<calculation>", description="12 / 2 * 3 + 14 - 1", aliases=["math", "calculate"])
    async def calc(self, ctx, *, calc):
        """
        Calculates the given calculation.

        '/' and '*' are divide and multiply respectively.
        """

        clean = re.compile(r'^[0-9+\-*/()]*$', re.IGNORECASE).findall(calc)

        if clean and re.compile(r'[.]{2,}', re.IGNORECASE).findall(calc):
            return await self.notice_embeds.error(ctx, "Invalid Math", "I could not calculate that")

        inp = re.sub(r"\.(?![0-9])", "", calc)

        try:
            mathed = eval(inp, {'__builtins__': None})

            e = discord.Embed(
                title=" :mobile_phone: Here's Your Calculation",
                color=discord.Color.green(),
                description=f"{calc} = **{mathed}**"
            )

            await ctx.reply(mention_author=False, embed=e)
        except (TypeError, SyntaxError):
            return await self.notice_embeds.error(ctx, "Invalid Math", "That Calculation Contains Syntax Errors")

    # Randint
    @commands.command(name="randint", aliases=["random", "num"],
                      brief="Picks between a random number.", usage="<min> <max>", description="31 69")
    async def _randint(self, ctx, _min: int, _max: int):
        num = random.randint(_min, _max)

        e = discord.Embed(
            title=":abacus: Random Number",
            color=discord.Color.green(),
            description=f"**It picked:** {num}"
        )

        await ctx.reply(mention_author=False, embed=e)

    # Minify
    @commands.group(name="minify", aliases=["compact", "compress"],
                    brief="Minify JavaScript or CSS code.", usage="<js/css> <code>",
                    description="js var x = 1;\na!minify css .selector { display: none; }")
    async def minify(self, ctx, ctype, *, code):
        if ctype not in ["js", "css"]:
            return await self.notice_embeds.error(ctx, "Error Minifying", "That is not a valid code type!")
        cmd = self.client.get_command(f"minify {ctype}")
        await ctx.invoke(cmd, code)

    @minify.command()
    async def js(self, ctx, code):
        code = code.replace("```js\n", "").replace("\n```", "").replace("```\n", "")
        res = requests.post("https://javascript-minifier.com/raw", data={"input": code})
        e = discord.Embed(
            title=":desktop: Here's Your Minified JavaScript",
            color=discord.Color.green(),
            description=f"```js\n{res.text}\n```"
        )
        await ctx.reply(embed=e)

    @minify.command()
    async def css(self, ctx, code):
        code = code.replace("```css\n", "").replace("\n```", "").replace("```\n", "")
        res = requests.post("https://cssminifier.com/raw", data={"input": code})
        e = discord.Embed(
            title=":desktop: Here's Your Minified CSS",
            color=discord.Color.green(),
            description=f"```css\n{res.text}\n```"
        )
        await ctx.reply(embed=e)
        
    @commands.command(brief="Create banner images by overlaying text over images of your choice.",
                      usage="<url/attachment> <color>, <header>, [text1], [text2]")
    async def banner(self, ctx, url, *, args):
        text1 = text2 = None
        split_args = args.split(", ")

        try:
            if not ctx.message.attachments:
                image = Image.open(requests.get(url, stream=True).raw)
            else:
                image = Image.open(requests.get(ctx.message.attachments[0].url, stream=True).raw)
            w, h = image.size
            if w < 1000 or h < 200:
                return await self.notice_embeds.error(ctx, "Image Too Small", "This image is too small.\n"
                                                                              "Please use an image that is "
                                                                              "at least 1000x200.")
            image = image.crop((w - (w-1152/4), h - (h-256/4), 3 * (w - (w-1152/4)), 3 * (h - (h-256/4))))
            w, h = image.size
        except Exception as e:
            return await self.notice_embeds.error(ctx, "Request Failure", "I could not fetch this image.\n"
                                                                          "Please try another one.\n\n"
                                                                          f"**{e.__class__.__name__}**")

        try:
            color = ImageColor.getcolor(split_args[0], "RGB")              
        except ValueError:
            if ctx.message.attachments:
                try:
                    color = ImageColor.getcolor(url[:-1], "RGB")
                except ValueError:
                    return await self.notice_embeds.error(ctx, "Invalid Color", "This is not a valid color.\nProvide your "
                                                                            "color in the following format: `#7848e6`")
            else:
                return await self.notice_embeds.error(ctx, "Invalid Color", "This is not a valid color.\nProvide your "
                                                                            "color in the following format: `#7848e6`")
        header = split_args[1]
        if ctx.message.attachments:
            header = split_args[0]
        try:
            text1 = split_args[2]
            text2 = split_args[3]
        except IndexError:
            if ctx.message.attachments:
                text1 = split_args[1]
                text2 = split_args[2]

        draw = ImageDraw.Draw(image)
        hfont = ImageFont.truetype(p + "/Nunito-Light.ttf", 72)
        tfont = ImageFont.truetype(p + "/Nunito-Light.ttf", 18)

        draw.text((w/2, h/2), header, color, hfont, anchor="mm")
        if text1:
            draw.text((w/2, h/2-50), text1, color, tfont, anchor="mm")
        if text2:
            draw.text((w/2, h/2+50), text2, color, tfont, anchor="mm")
        with open(f'{p}/out.png', 'wb') as f:
            image.save(f)

        e = discord.Embed(title="🖼️ Here Is Your Banner", color=discord.Colour.green())
        e.set_image(url=f"attachment://out.png")
        await ctx.reply(embed=e, file=discord.File(p + "/out.png"))

        if os.name == "nt":
            os.system(f"del {p}/out.png")
        else:
            os.system(f"rm {p}/out.png")
            
    @commands.command(brief="Read text from images.", usage="<attachment>")
    async def ocr(self, ctx):
        if not ctx.message.attachments:
            return await self.notice_embeds.error(ctx, "Error OCR-ing", "Please provide an attachment to OCR.")
        url = ctx.message.attachments[0].url        
        ocr = ocrspace.API(api_key=os.getenv("OCRSPACE"))
        res = ocr.ocr_url(url)
        e = discord.Embed(title="📄 Here Is Your OCR Result", 
                          description=f"```yaml\n{res}\n```", 
                          color=discord.Colour.green())
        await ctx.reply(embed=e)
        
    @commands.command(brief="Translate text across languages.", usage="<source> <destination> <text>")
    async def translate(self, ctx, source, destination, *, text):
        try:
            if source == "auto":
                res = self.translator.translate(text, dest=destination)
            else:
                res = self.translator.translate(text, src=source, dest=destination)    
        except ValueError as e:
            if str(e) == "invalid source language":
                return await self.notice_embeds.error(ctx, "Error Translating", 
                                                f"`{source}` is not a valid source language.")
            else:
                return await self.notice_embeds.error(ctx, "Error Translating", 
                                                f"`{destination}` is not a valid destination language.")
        e = discord.Embed(title="🈁 Here Is Your Translation", 
                          description=f"```yaml\n{res.text}\n```", 
                          color=discord.Colour.green())
        await ctx.reply(embed=e)

    @commands.group(brief="Encode and decode Base64 text.", usage="<encode/decode> <text>", aliases=["base64"])   
    async def b64(self, ctx):
        if ctx.subcommand_passed is None:
            return await self.notice_embeds.error(ctx, "Error Parsing", "Please provide `encode/decode`"
                                            "to parse this Base64.")
        if ctx.invoked_subcommand is None:
            return await self.notice_embeds.error(ctx, "Error Parsing", "That is not a valid action!")

    @b64.command()         
    async def encode(self, ctx, *, text):
        e = discord.Embed(
            title=":desktop: Here's Your Encoded Base64",
            color=discord.Color.green(),
            description=f"```\n{base64.b64encode(bytes(text, 'utf-8')).decode('utf-8')}\n```"
        )
        await ctx.reply(embed=e)

    @b64.command()         
    async def decode(self, ctx, *, text):
        text += '=' * (-len(text) % 4)
        try:
            e = discord.Embed(
                title=":desktop: Here's Your Decoded Base64",
                color=discord.Color.green(),
                description=f"```\n{base64.b64decode(bytes(text, 'utf-8')).decode('iso-8859-1')}\n```"
            )
        except (base64.binascii.Error):
            return await self.notice_embeds.error(ctx, "Error Parsing", "That is not a valid Base64!")
        await ctx.reply(embed=e)    


def setup(client):
    client.add_cog(Tools(client))
