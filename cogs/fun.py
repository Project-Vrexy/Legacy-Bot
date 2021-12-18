# StdLib
import random
from random import randint, choice
import os
import platform

# Discord
import nextcord as discord
from nextcord.ext import commands

# Third Party
from aiohttp import ClientSession
from emojifier import Emojifier
import ujson as json
import requests

# Local Code
from cogs.utils.reddit import RedditUtils
from cogs.utils.embeds import NoticeEmbeds


class EmbedDetails:
    def __init__(self, description, gauge):
        self.description = description
        self.gauge = gauge


class Fun(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.emoji = '🎉'
        self.desc = 'Commands that you can use to pass the time'

        self.reddit_utils = RedditUtils(client=client)
        self.notice_embeds = NoticeEmbeds(client=client)

        self.extras = {
            "8ball": {
                "examples": [
                    "PlaceDet Do you like Meon?"
                ]
            },
            "xkcd": {
                "examples": [
                    "PlaceDet python"
                ]
            }
        }

    # 8Ball
    @commands.command(name="8ball", brief="Ask the magic 8Ball a question.", usage="<question?>")
    async def _8ball(self, ctx, *, question):
        if question and question.endswith("?"):
            e = discord.Embed(
                title=":8ball: The Magic 8ball",
                color=discord.Color.green()
            )

            e.add_field(name="You Asked", value=question.capitalize())
            options = (
                "It is certain.",
                "It is decidedly so.",
                "Without a doubt.",
                "Yes – definitely.",
                "You may rely on it.",
                "As I see it, yes.",
                "Most likely.",
                "Outlook good.",
                "Yes.",
                "Signs point to yes.",
                "Reply hazy, try again.",
                "Ask again later.",
                "Better not tell you now.",
                "Cannot predict now.",
                "Concentrate and ask again.",
                "Don't count on it.",
                "My reply is no.",
                "My sources say no.",
                "Outlook not so good.",
                "Very doubtful."
            )

            e.add_field(name="It Answered",
                        value=choice(options), inline=False)

        else:
            e = discord.Embed(
                title=":8ball: The Magic 8ball",
                color=discord.Color.green(),
                description="I couldn't get the ball!"
            )

        await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # IQ
    @commands.command(brief='Get the IQ of a user.')
    async def iq(self, ctx, mention: discord.Member = None):
        if mention is None:
            mention = ctx.author

        def gstring(brain, empty):
            return brain * ':brain:' + empty * ':black_circle:'

        iq = randint(0, 300)

        if mention.id in self.client.owner_ids:
            iq = 300

        miq = int(iq / 25) | 0
        if miq > 10:
            miq = 10

        gauges = [
            EmbedDetails('Aeon has no hope for you', gstring(0, 10)),
            EmbedDetails('Life\'s been hard on you, I guess.', gstring(1, 9)),
            EmbedDetails('Go back to school', gstring(2, 8)),
            EmbedDetails('You\'re average.', gstring(3, 7)),
            EmbedDetails('you\'re smart doe :flushed:', gstring(4, 6)),
            EmbedDetails('You have ascended, not even Aeon can handle you', gstring(5, 5)),
            EmbedDetails('You have broken the lithosphere', gstring(6, 4)),
            EmbedDetails('You have broken the   hydrosphere', gstring(7, 3)),
            EmbedDetails('You have broken the atmosphere', gstring(8, 2)),
            EmbedDetails('You have broken the molten core', gstring(9, 1)),
            EmbedDetails('You have broken the fabric of spacetime', gstring(10, 0))
        ][miq]

        e = discord.Embed(
            title=f"IQ of {mention.name} is {iq}",
            color=discord.Color.green()
        )

        e.add_field(name=gauges.description, value=f"{gauges.gauge}")
        return await ctx.reply(mention_author=False, embed=e)

    # PP
    @commands.command(brief="Get the PP size of a user.", aliases=['cock', 'penis'])
    async def pp(self, ctx, mention: discord.Member = None):
        if mention is None:
            mention = ctx.author

        iq = randint(0, 300)

        trans = [632670854244728842, 478823932913516544, 348591272476540928]
        if mention.id in trans:
            iq = 0
        elif mention.id in self.client.owner_ids and not mention.id == 348591272476540928:
            iq = 300

        miq = int(iq / 25) | 0
        if miq > 10:
            miq = 10

        def gstring(brain, empty):
            return brain * ':white_circle:' + empty * ':black_circle:'

        gauges = [
            EmbedDetails('You are a woman', gstring(0, 10)),
            EmbedDetails('Ok, trans man.', gstring(1, 9)),
            EmbedDetails('Shut up, you cuck.', gstring(2, 8)),
            EmbedDetails('I can respect that.', gstring(3, 7)),
            EmbedDetails('You must get a lot of girls.', gstring(4, 6)),
            EmbedDetails('I think that\'s enough.', gstring(5, 5)),
            EmbedDetails('I said that\'s enough.', gstring(6, 4)),
            EmbedDetails('I said enough.', gstring(7, 3)),
            EmbedDetails('STOP IT I SAID ENOUGH IS ENOUGH', gstring(8, 2)),
            EmbedDetails('ENOUGH#(#)@)#(@($*@', gstring(9, 1)),
            EmbedDetails('I SAID ENOUGHAOWDEIWO(@)(@E)*!*(F@E93ie', gstring(10, 0))
        ][miq]

        e = discord.Embed(
            title=f"PP size of {mention.name} is {iq} inches",
            color=discord.Color.green()
        )

        e.add_field(name=gauges.description, value=gauges.gauge)
        return await ctx.reply(mention_author=False, embed=e)

    # Gay
    @commands.command(brief='Get the gayness of a user.')
    async def gay(self, ctx, mention: discord.Member = None):
        if mention is None:
            mention = ctx.author

        iq = randint(0, 300)

        if mention.id == self.client.owner_ids[1]:
            iq = 0
        elif mention.id in [478823932913516544, 348591272476540928]:
            iq = 300

        miq = int(iq / 25) | 0
        if miq > 10:
            miq = 10

        def gstring(brain, empty):
            return brain * ':rainbow_flag:' + empty * ':black_circle:'

        gauges = [
            EmbedDetails('You\'re as straight as my A.', gstring(0, 10)),
            EmbedDetails('You\'re an iPad pro bend.', gstring(1, 9)),
            EmbedDetails('You\'re super-straight.', gstring(2, 8)),
            EmbedDetails('You\'re average.', gstring(3, 7)),
            EmbedDetails('You\'re not really that straight.', gstring(4, 6)),
            EmbedDetails('You\'re bisexual.', gstring(5, 5)),
            EmbedDetails('You\'re kinda gay.', gstring(6, 4)),
            EmbedDetails('You\'re mostly gay.', gstring(7, 3)),
            EmbedDetails('You\'re almost gay.', gstring(8, 2)),
            EmbedDetails('You\'re gay.', gstring(9, 1)),
            EmbedDetails('You\'re the gay agenda I was warned about.', gstring(10, 0))
        ][miq]

        e = discord.Embed(
            title=f"Gayness of {mention.name} is {iq}",
            color=discord.Color.green()
        )

        e.add_field(name=gauges.description, value=gauges.gauge)
        return await ctx.reply(mention_author=False, embed=e)

    # Rate
    @commands.command(brief='Rate how epic a user is.')
    async def rate(self, ctx, mention: discord.Member = None):
        if mention is None:
            mention = ctx.author

        iq = randint(0, 10)

        if mention.id in self.client.owner_ids:
            iq = 10

        def gstring(brain, empty):
            return brain * ':heart:' + empty * ':black_heart:'

        gauges = [
            EmbedDetails('You\'re not epic at all.', gstring(10, 0)),
            EmbedDetails('You\'re not that epic.', gstring(1, 9)),
            EmbedDetails('You\'re kinda half-epic', gstring(2, 8)),
            EmbedDetails('You\'re mostly half-epic', gstring(3, 7)),
            EmbedDetails('You\'re getting there.', gstring(4, 6)),
            EmbedDetails('You\'re half-epic.', gstring(5, 5)),
            EmbedDetails('You\'re half-epic, but not epic at all.', gstring(6, 4)),
            EmbedDetails('You\'re half-epic, but not that epic.', gstring(7, 3)),
            EmbedDetails('You\'re kinda epic.', gstring(8, 2)),
            EmbedDetails('You\'re mostly epic.', gstring(9, 1)),
            EmbedDetails('You\'re epic.', gstring(10, 0))
        ][iq]

        e = discord.Embed(
            title=f"I rate {mention.name} {iq}/10",
            color=discord.Color.green()
        )

        e.add_field(name=gauges.description, value=gauges.gauge)
        return await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Urban
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.is_nsfw()
    @commands.command(brief="Get an Urban Dictionary definition.", usage="<word>",
                      help="`PlaceDeturban netflix and chill`" "\n`PlaceDeturban h`")
    async def urban(self, ctx, *, define):
        async with ClientSession() as session:
            uri = f"https://api.urbandictionary.com/v0/define?term={define}"

            async with session.get(uri) as ud:
                data = await ud.json()

                if len(data['list']) <= 0:
                    e = discord.Embed(
                        title=":x: Error Fetching Definition",
                        color=discord.Color.red(),
                        description="There is no such definition with that name."
                    )

                    return await ctx.reply(mention_author=False, embed=e)

                d = data['list'][randint(0, len(data['list']) - 1)]

                clean_definition = d['definition'].translate({91: '', 93: ''})
                clean_example = d['example'].translate({91: '', 93: ''})

                if len(clean_definition) >= 4087:
                    definition_split = [clean_definition[i:i + 4087] for i in range(0, len(clean_definition), 4087)]
                    prepared_definition = f"{definition_split[0]} `[CHAR]`"
                else:
                    prepared_definition = clean_definition

                if len(clean_example) >= 1015:
                    example_split = [clean_example[i:i + 1015] for i in range(0, len(clean_example), 1015)]
                    prepared_example = f"{example_split[0]} `[CHAR]`"
                else:
                    prepared_example = clean_example

                e = discord.Embed(
                    title=d['word'],
                    description=prepared_definition,
                    color=discord.Color.green(),
                    url=d['permalink']
                )

                e.add_field(name="Example", value=prepared_example)
                e.set_footer(text=f"👤 {d['author']} • 👍 {d['thumbs_up']} • 👎 {d['thumbs_down']}")

                url = "https://media.discordapp.net/attachments/713675042143076356/836903635685998682/unknown.png" \
                      "?width=676&height=676 "
                ud_url = "https://urbandictionary.com"

                e.set_author(name="Urban Dictionary", icon_url=url, url=ud_url)

                await ctx.reply(mention_author=False, embed=e)

    # Joke
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Tell a joke.")
    async def joke(self, ctx):
        async with ClientSession() as session:
            uri = "https://official-joke-api.appspot.com/random_joke"
            async with session.get(uri) as api:
                joke = await api.json()

                e = discord.Embed(
                    title=joke['setup'],
                    color=discord.Color.green(),
                    description=joke['punchline']
                )

                await ctx.reply(mention_author=False, embed=e)

    # --------------------------------

    # Meme
    @commands.command(brief="Get a meme from a random meme subreddit.")
    async def meme(self, ctx):
        options = ["DankMemes", "Memes", "OkBuddyRetard", "196"]

        await self.reddit_utils.multi_reddit(ctx, options)

    # XKCD
    @commands.command(brief="Gets an xkcd", usage="[xkcd name]")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def xkcd(self, ctx, *, name):
        async with ctx.channel.typing():
            api = requests.get(f"https://imgs.xkcd.com/comics/{name.lower().replace(' ', '_')}.png")

            if str(api.status_code).startswith("4"):
                return await self.notice_embeds.error(ctx, "Error fetching xkcd", "There is no xkcd with that name.")
            elif str(api.status_code).startswith("2"):
                with open('xkcd.png', 'wb') as img:
                    img.write(api.content)

                e = discord.Embed(
                    title=":frame_photo: Here's that xkcd",
                    color=discord.Color.green(),
                    description=name
                )

                e.set_image(url="attachment://xkcd.png")

                await ctx.reply(embed=e, file=discord.File('xkcd.png'), mention_author=None)
                os.system('del xkcd.png' if platform.system() == "Windows" else 'rm xkcd.png')
            else:
                return await self.notice_embeds.error(ctx, "Error fetching xkcd", "xkcd is down.")

    # --------------------------------

    # Emojify
    @commands.command(brief="Emojifies the given text")
    async def emojify(self, ctx, *, text=None):
        if text is None:
            text = "bro... you need text"

        with open(f"{self.client.json}/mappings.json", encoding="utf8") as f:
            mapping = json.load(f)

        emoji = Emojifier.of_custom_mappings(mapping)
        emojipasta = emoji.generate_emojipasta(text=text)

        if len(emojipasta) > 2040:
            split = [emojipasta[i: i + 2039] for i in range(0, len(emojipasta), 2039)]
            prepared_emojipasta = f"{split[0].replace('🇭🇭', '🇭')} `[CHAR]`"
        else:
            prepared_emojipasta = emojipasta.replace('🇭🇭', '🇭')

        e = discord.Embed(
            title="Emily ✨ BLM ACAB machine",
            description=prepared_emojipasta,
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Play Rock Paper scissors with Aeon.', usage='<rock/paper/scissors>')
    async def rps(self, ctx, go):
        ol = ["rock", "paper", "scissors"]
        if go.lower() not in ol:
            return await ctx.reply("that option doesn't exist what are you doing :flushed::flushed:")

        go = go.lower()
        bgo = random.choice(ol)
        pol = [bgo, go]  # a list of the two options, why not
        ret_str = "h"

        if pol in [["rock", "rock"], ["paper", "paper"], ["scissors", "scissors"]]:
            ret_str = "😳 We might have fucked up that. Try again."
        elif pol == ["scissors", "paper"]:
            ret_str = "✂ Sliced you right in half."
        elif pol == ["paper", "rock"]:
            ret_str = "📃 Your rock is gone."
        elif pol == ["rock", "scissors"]:
            ret_str = ":rock: Your scissors are absolutely bonked"
        elif pol == ["scissors", "rock"]:
            ret_str = ":scissors: My rock.. is destroyed."
        elif pol == ["rock", "paper"]:
            ret_str = "📃 My rock.. is destroyed."

        await ctx.send(ret_str if ret_str != "h" else str(pol))


def setup(client):
    client.add_cog(Fun(client))
