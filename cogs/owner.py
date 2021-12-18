# Stdlib
import asyncio
import inspect
import io
import math
import os
import sys
import textwrap
import time
import traceback
import subprocess
from contextlib import redirect_stdout
from datetime import datetime

# Discord
import nextcord as discord
from nextcord.ext import commands
from dislash import ActionRow, Button, ButtonStyle

# Third Party
from difflib import SequenceMatcher
import matplotlib.pyplot as plt
from pandas import read_json
import ujson as json

# Local Code
from cogs.utils.help import HelpMenus, HelpUtils
from cogs.utils.embeds import NoticeEmbeds, EmbedUtils
from cogs.utils.paginator import Paginator
from cogs.utils.path import path

# Paths
p = path()


# noinspection PyBroadException
class Owner(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.notice_embeds = NoticeEmbeds(client)
        self.embed_utils = EmbedUtils(client)
        self.help_menus = HelpMenus(client)
        self.help_utils = HelpUtils(client)

        self.extras = {
            'dev': {
                'reload': {
                    'examples': [
                        'PlaceDet all',
                        'PlaceDet fun'
                    ]
                }
            }
        }

    # Default
    @commands.is_owner()
    @commands.group(aliases=["sudo"], hidden=True, brief="Show dev commands if you didn't provide parameters.")
    async def dev(self, ctx):
        if ctx.invoked_subcommand is not None:
            return
        if ctx.subcommand_passed is None:
            return await ctx.invoke(self.client.get_command("dev help"))

        _commands = []
        dev_command = self.client.get_command(name='dev')
        s = None

        for command in dev_command.commands:
            _commands.append(command.name)
            _commands.extend(command.aliases)

        for c in _commands:
            cmd = dev_command.get_command(name=c)

            if cmd.enabled and not cmd.hidden:
                ratio = round(SequenceMatcher(a=ctx.subcommand_passed, b=cmd.name).ratio(), 1)

                if ratio >= 0.7:
                    s = cmd.name
                    break

        ctx.command.aliases.sort()
        gn = ctx.invoked_with

        if s is None:
            return await self.notice_embeds.error(ctx, "Subcommand Does Not Exist", f"Use `{ctx.prefix}{gn} help` to "
                                                                                    "view all subcommands.")
        else:
            return await self.notice_embeds.error(ctx, "Subcommand Does Not Exist", "Perhaps you meant to run "
                                                                                    f"`{ctx.prefix}{gn} {s}`?")

    # Help
    @dev.command(name="help", brief="List all dev commands in the bot.")
    async def _help(self, ctx):
        await self.help_menus.paginated_menu(
            context=ctx, group_get='dev',
            title=':question: Aeon Dev Help',
            description='These commands are developer only.\nThey should only be run in private servers.'
        )

    # Eval
    @dev.command(name='eval', brief="Execute and evaluate code.", usage="<code>")
    async def _eval(self, ctx, *, body=None):
        load = await self.notice_embeds.load(ctx, 'Evaluating')

        if body is None:
            return await self.notice_embeds.load_error(load, 'Error Evaluating', 'I need code to be able to evaluate.')

        if 'C:\\\\Users' in body:
            return await ctx.send('bro...')

        # evaluate and execute python code
        env = {
            'ctx': ctx,
            'client': self.client,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            'source': inspect.getsource,
            'version': sys.version,
            'self': self,
            'processpath': p,
            'processid': p[24:]
        }

        async def cleanup_code(content):
            if content.startswith('```') and content.endswith('```'):
                return content.replace("```py\n", "").replace("\n```", "")

            return content

        env.update(globals())
        body = await cleanup_code(body)
        stdout = io.StringIO()
        err = None
        out = None
        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            err = f'{e}'
            errtype = e.__class__.__name__
            ed = discord.Embed(title=":x: You made an error!", description=f"```py\n{err}```",
                               color=discord.Colour.red())
            ed.set_footer(text=errtype)
            return await load.edit(embed=ed)

        func = env['func']
        try:
            errtype = None
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            err = f'```py\n{value}{traceback.format_exc()}```'
            errtype = e.__class__.__name__

        else:
            value = stdout.getvalue()
            if ret is None:
                if value:
                    out = f"{value}"
            else:
                out = f'{value}{ret}'

        if out:
            await load.delete()

            if len(out) > 4087:
                out = [out[i:i + 4087] for i in range(0, len(out), 4087)]
                pages = []

                for i in range(0, len(out)):
                    out_chunk = out[i]

                    e = discord.Embed(
                        title=":white_check_mark: Here you go!",
                        description=f"```py\n{out_chunk}\n```",
                        color=discord.Color.green()
                    )

                    e.set_footer(text=f"Page {i + 1}/{len(out)}")
                    pages.append(e)

                paginator = Paginator(self.client, ctx, pages, timeout=240)
                await paginator.run()
            else:
                e = discord.Embed(
                    title=":white_check_mark: Here you go!",
                    description=f"```py\n{out}\n```",
                    color=discord.Color.green()
                )

                await ctx.reply(embed=e, mention_author=False)

        elif err:
            await load.delete()
            e = discord.Embed(title=":x: You Made An Error", description=f"{err}",
                              color=discord.Colour.red())
            e.set_footer(text=errtype)
            return await ctx.reply(mention_author=False, embed=e)
        else:
            await load.delete()
            return

    # H
    @dev.command(brief="Post H.", usage=" ")
    async def h(self, ctx):
        await ctx.send("h")

    # Insert
    @dev.command(brief="Insert the current graph data.", usage="")
    async def insert(self, ctx):
        day = datetime.now().strftime("%d")
        try:
            with open(p + "/data/json/stats.json", "r") as fw:
                stats = json.load(fw)
                test = stats['servers'][f'{day}']
                print(f"{test} - checking for KeyError")  # pycharm pls stop warning me
        except KeyError:
            with open(p + "/data/json/stats.json") as fw:
                stats = json.load(fw)
                stats['servers'][f'{day}'] = len(self.client.guilds)
                stats['users'][f'{day}'] = len(self.client.users)
        else:
            return await ctx.reply(":x: The server and user data for today already exists!")
        if day == '01':
            channel = self.client.get_channel(837393740279709697)
            if len(stats['servers']) < 30 or len(stats['users']) < 30:
                e = discord.Embed(title=":calendar: It's a new month,  so...",
                                  description="It's time for your monthly statistics!\n"
                                              "The following graph is truncated because not enough data was provided"
                                              "for this month.",
                                  color=discord.Colour.green())
            else:
                e = discord.Embed(title=":calendar: It's a new month,  so...",
                                  description="It's time for your monthly statistics!", color=discord.Colour.green())
            e.set_image(url="attachment://graph.png")
            await channel.send(embed=e, file=discord.File(p + "/graph.png"))
            empty = {'servers': {}, 'users': {}}
            with open(p + "/data/json/stats.json", "w") as fw:
                json.dump(empty, fw, indent=4)
        else:
            with open(p + "/data/json/stats.json", "w") as fw:
                json.dump(stats, fw, indent=4)
        await ctx.reply(":white_check_mark: The server and user data for today was inserted.")

    # Shell
    @dev.command(brief="Run a shell command and capture its output.", usage="<command>")
    async def shell(self, ctx, *, cmd=None):  # sourcery no-metrics
        load = await self.notice_embeds.load(ctx, 'Executing')
        if cmd is None:
            return await self.notice_embeds.load_error(load, 'Error',
                                                       'You need to type some shell command to execute first.')
        sh = "/bin/zsh"  # change this to /bin/bash if you don't have zsh on your VPS
        res = subprocess.Popen(cmd, shell=True, executable=sh, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = res.communicate()
        stdout = stdout.decode('utf-8').rstrip("\r|\n")
        stderr = stderr.decode('utf-8').rstrip("\r|\n")
        stdout = [stdout[i:i + 1990] for i in range(0, len(stdout), 1990)]
        stderr = [stderr[i:i + 1990] for i in range(0, len(stderr), 1990)]
        if stdout and not stderr:
            embs = []
            if len(stdout) > 1:
                for pg, chunk in enumerate(stdout, start=1):
                    e = discord.Embed(title=":white_check_mark: Success",
                                      description=f"Here is the result of the command:\n```sh\n{chunk}\n```",
                                      color=discord.Colour.green())
                    e.set_footer(text=f"Page {pg}/{len(stdout)}")
                    embs.append(e)
                    paginator = Paginator(self.client, ctx, embs, timeout=240)
                    await paginator.run()
            else:
                e = discord.Embed(title=":white_check_mark: Success",
                                  description=f"Here is the result of the command:\n```sh\n{stdout[0]}\n```",
                                  color=discord.Colour.green())
                await load.edit(embed=e)
        elif stderr and not stdout:
            e = None
            embs = []
            if len(stderr) > 1:
                for pg, chunk in enumerate(stderr, start=1):
                    e = discord.Embed(title=":x: Failure",
                                      description=f"Here is the error that occurred:\n```sh\n{chunk}\n```",
                                      color=discord.Colour.red())
                    e.set_footer(text=f"Page {pg}/{len(stderr)}")
                    embs.append(e)
                    paginator = Paginator(self.client, ctx, embs, timeout=240)
                    await paginator.run()
            else:
                e = discord.Embed(title=":x: Failure",
                                  description=f"Here is the error that occurred:\n```sh\n{stderr[0]}\n```",
                                  color=discord.Colour.red())
            await load.edit(embed=e)
        else:
            e = discord.Embed(title=":x: Error",
                              description="An unexpected issue occurred executing this command.",
                              color=discord.Colour.red())
            await load.edit(embed=e)

    # Raise
    @dev.command(name="raise", brief="Raise an error for development purposes", usage="<error>")
    async def _raise(self, ctx, *, error):
        await ctx.message.add_reaction("✅")
        raise Exception(error)

    # Reload
    @dev.command(brief="Reload a cog.", usage="<cog/all>")
    async def reload(self, ctx, cog_to_reload):  # sourcery no-metrics
        suggestion = None
        if cog_to_reload == 'all':
            start = time.time()
            cogs = 0
            msg = await self.notice_embeds.load(ctx, 'Reloading cogs')

            for cog in list(self.client.cogs):
                cogs += 1
                if cog == "Music":
                    cogs -= 1
                    continue

                self.client.reload_extension(f'cogs.{cog.lower().replace("_", "")}')
            end = time.time()

            e = discord.Embed(
                title=":white_check_mark: Done",
                description="Finished reloading.",
                color=discord.Color.green()
            )

            e.add_field(name="Reloaded", value=f"{cogs} cogs")
            e.add_field(name="Elapsed", value=f"{math.trunc((end - start) * 100)}ms")
        else:
            if cog_to_reload.lower() == 'music':
                return await self.notice_embeds.error(ctx, 'Error Reloading', f"`{cog_to_reload}` cannot be reloaded.")

            start = time.time()
            msg = await self.notice_embeds.load(ctx, f'Reloading {cog_to_reload}')

            if cog_to_reload not in [cog.lower().replace("_", "") for cog in self.client.cogs]:
                if cog_to_reload in [str(command).lower().replace("_", "") for command in self.client.commands]:
                    return await self.notice_embeds.load_error(
                        msg, 'Error Reloading',
                        f"`{cog_to_reload}` is a valid command but unloading individual commands is not supported"
                    )

                for botcog in [cog.lower().replace("_", "") for cog in self.client.cogs]:
                    ratio = round(SequenceMatcher(a=cog_to_reload, b=botcog).ratio(), 1)

                    if ratio >= 0.7:
                        suggestion = botcog
                        break

                if suggestion is None:
                    return await self.notice_embeds.load_error(msg, 'Error Reloading',
                                                               f"`{cog_to_reload}` is not a valid cog.")
                else:
                    return await self.notice_embeds.load_error(msg, 'Error Reloading',
                                                               f"`{cog_to_reload}` is not a valid cog. "
                                                               f"Perhaps you meant `{suggestion}`?")

            self.client.reload_extension(f'cogs.{cog_to_reload}')
            end = time.time()
            e = discord.Embed(
                title=":white_check_mark: Success",
                description=f"Reloaded `{cog_to_reload}` in {math.trunc((end - start) * 100)}ms",
                color=discord.Color.green()
            )

        await msg.edit(embed=e)
        await ctx.message.add_reaction("✅")
        return

    # Unload
    @dev.command(brief="Unloads a cog", usage="<cog>")
    async def unload(self, ctx, cog_to_reload):
        suggestion = None
        if cog_to_reload.lower() in ['music', 'owner']:
            return await self.notice_embeds.error(ctx, 'Error Unloading', f"`{cog_to_reload}` cannot be unloaded.")

        start = time.time()
        msg = await self.notice_embeds.load(ctx, f'Unloading {cog_to_reload}')

        if cog_to_reload not in [cog.lower().replace("_", "") for cog in self.client.cogs]:
            if cog_to_reload in [str(command).lower().replace("_", "") for command in self.client.commands]:
                return await self.notice_embeds.load_error(
                    msg, 'Error Reloading',
                    f"`{cog_to_reload}` is a valid command but loading individual commands is not supported"
                )

            for botcog in [cog.lower().replace("_", "") for cog in self.client.cogs]:
                ratio = round(SequenceMatcher(a=cog_to_reload, b=botcog).ratio(), 1)

                if ratio >= 0.7:
                    suggestion = botcog
                    break

            if suggestion is None:
                return await self.notice_embeds.load_error(msg, 'Error Unloading',
                                                           f"`{cog_to_reload}` is not a valid cog.")
            else:
                return await self.notice_embeds.load_error(msg, 'Error Unloading',
                                                           f"`{cog_to_reload}` is not a valid cog. "
                                                           f"Perhaps you meant `{suggestion}`?")

        self.client.unload_extension(f'cogs.{cog_to_reload}')
        end = time.time()
        e = discord.Embed(
            title=":white_check_mark: Success",
            description=f"Unloaded `{cog_to_reload}` in {math.trunc((end - start) * 100)}ms",
            color=discord.Color.green()
        )

        await msg.edit(embed=e)
        await ctx.message.add_reaction("✅")
        return

    # Load
    @dev.command(brief="Loads a cog", usage="<cog>")
    async def load(self, ctx, cog_to_reload):
        if cog_to_reload.lower() in ['music', 'owner']:
            return await self.notice_embeds.error(ctx, 'Error Loading', f"`{cog_to_reload}` cannot be loaded.")

        start = time.time()
        msg = await self.notice_embeds.load(ctx, f'Loading {cog_to_reload}')

        if cog_to_reload in [cog.lower().replace("_", "") for cog in self.client.cogs]:
            return await self.notice_embeds.load_error(msg, 'Error Loading', f"`{cog_to_reload}` is already a loaded "
                                                                             f"cog.")
        elif f"{cog_to_reload}.py" not in os.listdir(p + "/cogs"):
            return await self.notice_embeds.load_error(msg, "Error Loading", f"`{cog_to_reload}` does not exist.")

        self.client.load_extension(f'cogs.{cog_to_reload}')
        end = time.time()
        e = discord.Embed(
            title=":white_check_mark: Success",
            description=f"Loaded `{cog_to_reload}` in {math.trunc((end - start) * 100)}ms",
            color=discord.Color.green()
        )

        await msg.edit(embed=e)
        await ctx.message.add_reaction("✅")
        return

    # Reboot
    @dev.command(brief="Restart the bot.", usage=" ")
    async def reboot(self, ctx):
        buttons = ActionRow(
            Button(style=ButtonStyle.green, custom_id="accept", label="Yes"),
            Button(style=ButtonStyle.red, custom_id="ignore", label="No")
        )
        disabled_buttons = ActionRow(
            Button(style=ButtonStyle.green, custom_id="accept", label="Yes", disabled=True),
            Button(style=ButtonStyle.red, custom_id="ignore", label="No", disabled=True)
        )

        msg = await ctx.reply("This will reboot the bot, continue?", components=[buttons], mention_author=False)
        events = msg.create_click_listener(timeout=10)

        @events.matching_id("accept")
        async def reboot(inter):
            await inter.reply(type=7,
                              content="<a:load:827975573443051570> Rebooting bot...", components=[disabled_buttons])
            await ctx.message.add_reaction("✅")

            channel = self.client.get_channel(826732008805236737)
            now = datetime.now()
            e = discord.Embed(
                    title="<:offline:747395931875573781> Process Exited",
                    color=discord.Color.green(),
                    description=f"**Process started at:** {now.strftime('%Y/%m/%d %H:%M:%S')}"
            )
            await channel.send(embed=e)
            events.kill()
            os.execl(sys.executable, sys.executable, *sys.argv)
            sys.exit()

        @events.matching_id("ignore")
        async def ignore(inter):
            await inter.reply(type=7, content="Ok, not doing that then.", components=[disabled_buttons])
            events.kill()

        @events.timeout
        async def timeout():
            await msg.edit(content="Ok, not doing that then.", components=[disabled_buttons])

    # Exit
    @dev.command(brief="Stop the Bot.", usage=" ")
    async def exit(self, ctx):
        buttons = ActionRow(Button(style=ButtonStyle.green, custom_id="accept", label="Yes"),
                            Button(style=ButtonStyle.red, custom_id="ignore", label="No"))
        disabled_buttons = ActionRow(
            Button(style=ButtonStyle.green, custom_id="accept", label="Yes", disabled=True),
            Button(style=ButtonStyle.red, custom_id="ignore", label="No", disabled=True)
        )
        msg = await ctx.reply("This will exit the bot, continue?", components=[buttons], mention_author=False)
        events = msg.create_click_listener(timeout=10)

        @events.matching_id("accept")
        async def stop(inter):
            await inter.reply(type=7,
                              content="<a:load:827975573443051570> Exiting bot...", components=[disabled_buttons])
            await ctx.message.add_reaction("✅")

            channel = self.client.get_channel(826732008805236737)
            now = datetime.now()

            e = discord.Embed(
                title="<:offline:747395931875573781> Process Exited",
                color=discord.Color.green(),
                description=f"**Process started at:** {now.strftime('%Y/%m/%d %H:%M:%S')}"
            )

            await channel.send(embed=e)
            events.kill()
            self.client.unload_extension("cogs.events")
            sys.exit()

        @events.matching_id("ignore")
        async def ignore(inter):
            await inter.reply(type=7, content="Ok, not doing that then.", components=[disabled_buttons])
            events.kill()

        @events.timeout
        async def timeout():
            await msg.edit(content="Ok, not doing that then.", components=[disabled_buttons])

    # Graph
    @dev.command(brief="Graph the user and server counts.", usage="")
    async def graph(self, ctx):
        axes = None

        class NotEnoughValuesError(Exception):
            pass

        h = await ctx.reply("<a:load:827975573443051570> Graphing...")
        stats = read_json(p + "/data/json/stats.json")

        for _ in range(2):
            fig, axes = plt.subplots(nrows=2, ncols=1, figsize=(9, 9))
            fig.set_facecolor("#202225")
            for param in ['text.color', 'axes.labelcolor', 'xtick.color', 'ytick.color']:
                plt.rcParams[param] = "#dcddde"
            plt.rcParams['axes.facecolor'] = "#2f3136"
            plt.rcParams['legend.facecolor'] = "#202225"
            [i.set_color("#dcddde") for i in plt.gca().get_xticklabels()]
        try:
            stats["servers"].plot(ax=axes[0], xlabel="Day of the Month", ylabel="Guild Count",
                                  title=f"Guild Count Over Time\n[Currently {stats['servers'].iloc[-1]}]",
                                  color=(0.18, 0.8, 0.439))
            stats["users"].plot(ax=axes[1], xlabel="Day of the Month", ylabel="User Count",
                                title=f"User Count Over Time\n[Currently {stats['users'].iloc[-1]}]",
                                color=(0.18, 0.8, 0.439))
        except IndexError:
            raise NotEnoughValuesError("no values available to plot")
        if len(stats['servers']) < 2:
            raise NotEnoughValuesError("not enough values to plot")

        plt.subplots_adjust(hspace=0.5)

        current = datetime.utcnow()
        initial = datetime(year=current.year, month=current.month, day=current.day)

        difference = current - initial
        hour = int(difference.total_seconds() / 3600)

        plt.figtext(0.5, 0.98, "All dates are in UTC", ha="center", fontsize=10)

        plt.figtext(0.5, 0.03, f"Last updated {hour} hours ago", ha="center", fontsize=14, weight="bold")
        plt.figtext(0.01, 0.01, current.strftime("%H:%M:%S %d/%m/%Y"), fontsize=12)
        plt.figtext(0.5, 0.01, "Data updates every day at 00:00", ha="center", fontsize=10)

        plt.savefig(p + "/graph.png")
        await h.delete()
        e = discord.Embed(title="📈 Here's your graph:", color=discord.Colour.green())
        e.set_image(url='attachment://graph.png')
        await ctx.reply(embed=e, file=discord.File(p + "/graph.png"), mention_author=False)

        # if platform.system() == "Windows":
        #     os.system('del graph.png')
        # else:
        #     os.system('rm graph.png')

    # Servers
    @dev.command(brief="Get the list of servers the bot is in.", usage="[create]")
    async def servers(self, ctx, create=False):  # sourcery no-metrics
        message = await ctx.reply("<a:load:827975573443051570> Loading...")
        sliced_guilds = [self.client.guilds[i:i + 6] for i in range(0, len(self.client.guilds), 6)]
        embeds_l = []
        for nm, li in enumerate(sliced_guilds):
            e = discord.Embed(title="Here you go!",
                              description=f"Shown {(nm + 1) * len(sliced_guilds[0])}/{len(self.client.guilds)} guilds"
                              if (nm + 1) * len(
                                  sliced_guilds[0]) < len(
                                  self.client.guilds) else f"Shown {len(self.client.guilds)}/{len(self.client.guilds)} "
                                                           "guilds",
                              color=discord.Colour.green())
            e.set_footer(text=f"Page {nm + 1}/{len(sliced_guilds)}")

            for guild in li:
                try:
                    invites = await guild.invites()
                except discord.Forbidden:
                    if create:
                        try:
                            channel = [channel for channel in guild.channels if type(channel) is discord.TextChannel][0]
                            invite = await channel.create_invite(max_age=3600)
                            invites = [invite]
                        except discord.Forbidden:
                            invites = None
                    else:
                        invites = None
                data = [(attr.upper().replace("_", ""), getattr(guild, attr)) for attr in dir(guild) if
                        attr in ["id", "owner", "name", "member_count"]]
                try:
                    data.append(("INVITE", invites[0]))
                except (IndexError, TypeError):
                    print(f"Invite fetching for {guild.name} failed!")
                    data.append(("INVITE", None))
                e.add_field(name=data[2][1],
                            value=f"```yaml\n{data[0][0]}: {data[0][1]}\n{data[1][0]}: {data[1][1]}\n{data[3][0]}:" 
                                  f"{data[3][1]}\n{data[4][0]}: {data[4][1]}\n```")
            embeds_l.append(e)
        await message.delete()
        pag = Paginator(self.client, ctx, embeds_l)
        await pag.run()

    # Dash
    @dev.command(brief="Private information for the bot.", usage=" ")
    async def dash(self, ctx):
        pe = discord.Embed(
            title=":information_source: Dev Info",
            color=discord.Color.green(),
            description="You should check your DMs!"
        )

        pe.add_field(name="Something.Host Dashboard", value="https://cp.something.host")
        pe.add_field(name="Private GitHub Repo", value="https://github.com/bruh-moment-funnies/Aeon")

        de = discord.Embed(
            title=":information_source: Secret Info",
            color=discord.Color.green(),
            description="Do not post these anywhere else! You'll get fired from the developer position."
        )

        de.add_field(name="\u200b", value="**:desktop: VPS**", inline=False)
        de.add_field(name="Host", value="sftp://199.127.61.178")
        de.add_field(name="Port", value="23")
        de.add_field(name="Username", value="service_7147")
        de.add_field(name="Password", value="eyJ0eXAiOiJKV1QiLCJhbGciOiJFUzI1NiJ9.eyJzdWIiOiIxNTUxMCIsImlzcyI6InNvbWV0aGluZ19jcCIsImlhdCI6MTYxNTIwMjY3Nn0.sxk1WvRGj0nHTFOtWq9MthuI3BcBHY8tgeWdNQhDfc5WyymkVEklA-RZhMEYMuVT18g8x28r06TV35FZNPoM0A")
        de.add_field(name="\u200b", value="**:control_knobs:  Panel**", inline=False)
        de.add_field(name="Link", value="https://cp.something.host/services/7147")
        de.add_field(name="\u200b", value="**:robot: Bot**", inline=False)
        de.add_field(name="Token", value=f"||{self.client._get_websocket(ctx.guild.id).token}||")

        await ctx.reply(embed=pe, mention_author=False)
        await ctx.author.send(embed=de)

        await ctx.message.add_reaction("✅")

    # Disable
    @dev.command(aliases=["toggle"], brief="Disable and enable commands globally.", usage="[command]")
    async def disable(self, ctx, *, command=None):
        if command is None:
            fc = [comms.name for comms in self.client.commands if comms.enabled is False]
            dev_disable_pages = []

            if not fc:
                fc = ["There are no disabled commands"]

            fc.sort()
            split_fc = await self.help_utils.page_split(fc, 25)

            for i in range(len(split_fc)):
                chunk = split_fc[i]
                e = discord.Embed(
                    title=":x: Disabled Commands",
                    color=discord.Color.green(),
                    description=f"These commands are disabled in the bot."
                    f"\n```yaml\n{', '.join(chunk)}```"
                    f"Use `{ctx.prefix}{ctx.command} [command]` to add or remove commands."
                )

                e.set_footer(text=f"Page {i + 1}/{len(split_fc)} - {len(fc)} disabled commands")
                dev_disable_pages.append(e)

            paginator = Paginator(self.client, ctx, dev_disable_pages)
            await paginator.run()
        else:
            cmd = self.client.get_command(name=command.lower())

            if cmd is None:
                await self.notice_embeds.error(ctx, "Error Disabling", "There is no command with that name")

            if 'dev' in command:
                e = discord.Embed(
                    title=":x: Error disabling",
                    color=discord.Color.red(),
                    description="You can't disable me, silly."
                )

                return await ctx.reply(embed=e, mention_author=False)

            if not cmd.enabled:
                cmd.enabled = True
                await ctx.reply(f"<a:success:827811351086366720> Enabled `{command}`", mention_author=False)
            else:
                cmd.enabled = False
                await ctx.reply(f"<a:success:827811351086366720> Disabled `{command}`", mention_author=False)

    # Update
    @dev.command(brief="Force a `git pull` in the bot.", usage=" ")
    async def update(self, ctx):
        msg = await ctx.reply("This will reboot the bot, continue?")
        try:
            h = await self.client.wait_for('message', check=lambda messages: messages.content == 'y',
                                           timeout=10)
        except asyncio.TimeoutError:
            await msg.edit(content="OK, not doing that then.")
            return
        if h:
            await ctx.reply("<a:load:827975573443051570> Rebooting bot...")
            await ctx.message.add_reaction("✅")
            channel = self.client.get_channel(826732008805236737)
            now = datetime.now()

            e = discord.Embed(
                title="<:offline:747395931875573781> Process Exited",
                color=discord.Color.green(),
                description=f"**Process started at:** {now.strftime('%Y/%m/%d %H:%M:%S')}"
            )

            await channel.send(embed=e)
            os.popen("git pull").read()
            os.execl(sys.executable, sys.executable, *sys.argv)
            sys.exit()

    @dev.command(brief="Posts a changelog.")
    async def post(self, ctx):
        with open(f"{self.client.json}/changelog.json") as changelog:
            changelog = json.load(changelog)

        channel = await self.client.fetch_channel(822391869714464798)
        changes = changelog[0]
        s = '\n'

        total_section = ""
        for count, section in enumerate(changes['changes']):
            if count == 0:
                total_section += f"**{section['title']}**\n{s.join(section['changes'])}"
            else:
                total_section += f"**\n\n{section['title']}**\n{s.join(section['changes'])}"

        e = discord.Embed(
            title=f":information_source: What's new in Aeon for {changes['date']}",
            description=total_section,
            color=discord.Color.green()
        )

        try:
            e.set_image(url=changes['image'])
        except KeyError:
            pass

        message = await channel.send(content="<@&837343560474951681>", embed=e)
        await message.publish()

        await ctx.reply("Posted changelog.", mention_author=False)


def setup(client):
    client.add_cog(Owner(client))
