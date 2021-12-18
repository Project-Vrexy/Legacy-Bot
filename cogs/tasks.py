# StdLib
from random import choice
import sqlite3
from datetime import datetime

# Discord
import nextcord as discord
from nextcord import Color, Embed
from nextcord.ext import commands, tasks

# Third Party
import matplotlib.pyplot as plt
from pandas import read_json
from ujson import load, dump
from cogs.utils.path import path

# Paths
p = path()

# Connections
con = sqlite3.connect(p + '/data/db/database.sqlite3')
cur = con.cursor()


class Tasks(commands.Cog):
    def __init__(self, client):
        self.client = client
        self.statistics_logger.start()
        self.remind.start()
        self.unban.start()
        self.clear_exceptioned_commands.start()

    # Cancel when unloaded
    def cog_unload(self):
        self.statistics_logger.cancel()
        self.remind.cancel()
        self.unban.cancel()
        self.clear_exceptioned_commands.start()

    # Statistics Logger
    @tasks.loop(minutes=1)
    async def statistics_logger(self):
        axes = None
        day = datetime.now().strftime("%d")
        with open(p + "/data/json/stats.json") as fw:
            stats = load(fw)
            stats['servers'][f'{day}'] = len(self.client.guilds)
            stats['users'][f'{day}'] = len(self.client.users)
        current_time = datetime.now().time().strftime("%H:%M")
        if current_time == '00:00':
            if day == '01':
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
                                          color=(0.204, 0.596, 0.859))
                    stats["users"].plot(ax=axes[1], xlabel="Day of the Month", ylabel="User Count",
                                        title=f"User Count Over Time\n[Currently {stats['users'].iloc[-1]}]",
                                        color=(0.204, 0.596, 0.859))
                except IndexError:
                    pass

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
                channel = self.client.get_channel(837393740279709697)
                if len(stats['servers']) < 30 or len(stats['users']) < 30:
                    e = discord.Embed(title=":calendar: It's a new month,  so...",
                                      description="It's time for your monthly statistics!\nThe following graph is "
                                                  "truncated "
                                                  "because not enough data was provided for this month.",
                                      color=discord.Colour.green())
                else:
                    e = discord.Embed(title=":calendar: It's a new month,  so...",
                                      description="It's time for your monthly statistics!", color=discord.Colour.blue())
                e.set_image(url="attachment://graph.png")
                await channel.send(embed=e, file=discord.File(p + "/graph.png"))
                empty = {'servers': {}, 'users': {}}
                with open(p + "/data/json/stats.json", "w") as ffw:
                    dump(empty, ffw, indent=4)
            else:
                with open(p + "/data/json/stats.json", "w") as fw:
                    dump(stats, fw, indent=4)
                    
    # Reminders task
    @tasks.loop(minutes=1)
    async def remind(self):
        with con:
            cur.execute(f"SELECT * FROM reminders")
            records = cur.fetchall()

            if len(records) <= 0:
                return

            f_str = '%Y-%m-%d %H:%M:%S'
            for row in records:
                curr = datetime.now()
                f_curr = str(curr.strftime(f_str))

                expir = datetime.strptime(row[3], f_str)
                f_expir = str(expir.strftime(f_str))

                if datetime.strptime(f_curr, f_str) >= datetime.strptime(f_expir, f_str):
                    user = await self.client.fetch_user(int(row[1]))
                    channel = await user.create_dm()

                    m = [
                        f"th're {user.name}, st. Aeon hast a message f'r thee!",
                        "'Ey There! I got a reminder for you.",
                        "Ding Ding!",
                        "Yo! hey dare! Peep this shit! ya got thahngs ta does!",
                    ]

                    e = Embed(
                        title=f":bell: {choice(m)}",
                        color=Color.green(),
                        description=row[2]
                    )

                    await channel.send(embed=e)
                    cur.execute(f"DELETE FROM reminders WHERE id = :id", {
                        'id': row[0]
                    })

    # Unban Task
    @tasks.loop(minutes=1)
    async def unban(self):
        with con:
            cur.execute(f"SELECT * FROM tempbans")
            records = cur.fetchall()

            if len(records) <= 0:
                return

            f_str = '%Y-%m-%d %H:%M:%S'
            for row in records:
                curr = datetime.now()
                f_curr = str(curr.strftime(f_str))

                expir = datetime.strptime(row[3], f_str)
                f_expir = str(expir.strftime(f_str))

                if datetime.strptime(f_curr, f_str) < datetime.strptime(
                        f_expir, f_str
                ):
                    return
                user = self.client.get_user(int(row[2]))
                mod = self.client.get_user(int(row[1]))

                guild = self.client.get_guild(int(row[0]))
                bans = await guild.bans()

                if user in bans:
                    await guild.unban(user, reason=f"Auto-unban by Aeon on behalf of {mod}")

                    channel = await self.client.fetch_channel(837393740279709697)
                    await channel.send('the')

                cur.execute(f"DELETE FROM tempbans WHERE guild = :guild AND user = :user", {
                    'guild': row[0],
                    'user': row[2]
                })

    # Discord Bot List Task
    @tasks.loop(minutes=5)
    async def update_stats(self):
        pass

    # Clear Exceptioned Commands
    @tasks.loop(minutes=5)
    async def clear_exceptioned_commands(self):
        with open(f"{self.client.json}/blocked.json") as json:
            data = load(json)

        data['commands'] = {}

        with open(f"{self.client.json}/blocked.json", "w") as json:
            dump(data, json, indent=4)


def setup(client):
    client.add_cog(Tasks(client))
