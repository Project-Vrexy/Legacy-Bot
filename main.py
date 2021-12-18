# StdLib
from os import listdir, getenv, chdir
from platform import system

# Discord
from nextcord import Intents
from nextcord.ext.commands import when_mentioned_or, AutoShardedBot
from dislash import InteractionClient

# Third Party
from dotenv import load_dotenv
from aiosqlite import connect, OperationalError

# Local
from cogs.utils.path import path

# Paths
p = path()
chdir(p)

# Config
load_dotenv(p + "/.env")

owners = [348591272476540928, 603635602809946113]
intents = Intents.default()
# noinspection PyUnresolvedReferences, PyDunderSlots
intents.members = True


# Prefix Code
async def get_prefix(bot, message):
    if not message.guild:
        return when_mentioned_or(bot.prefix)(bot, message)  # returns the default prefix

    try:
        async with connect(bot.db) as db:
            async with await db.execute('SELECT prefix FROM config WHERE id = :id', {'id': message.guild.id}) as cur:
                guild_prefix = await cur.fetchone()

        if len(guild_prefix) != 0:
            return when_mentioned_or(guild_prefix[0])(client, message)  # returns the current configured prefix

        return when_mentioned_or(client.prefix)(client, message)  # returns the default prefix
    except Exception:
        return when_mentioned_or(client.prefix)(client, message)  # ensure we have a usable prefix


# Client Creation
client = AutoShardedBot(
    command_prefix=get_prefix,
    intents=intents,
    owner_ids=[348591272476540928, 603635602809946113],
    case_insensitive=True,
    help_command=None
)

InteractionClient(client)

client.prefix = 'a!' if system() == "Linux" else 'ad!'
client.db = p + '/data/db/database.sqlite3'
client.json = p + '/data/json'

# Files
print("==== Cogs ====")
[(client.load_extension(f"cogs.{file[:-3]}"), print(f"Loaded: {file[:-3].title().replace('Nsfw', 'NSFW')}")) for file
 in listdir(p + "/cogs") if file.endswith(".py") and not file.startswith("economy")]    

if system() == "Linux":
    client.unload_extension("cogs.slashtest")

# Run the client
client.run(getenv("STABLE_TOKEN") if system() == "Linux" else getenv("ALPHA_TOKEN"))
