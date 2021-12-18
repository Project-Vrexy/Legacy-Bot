# StdLib
import random
from random import randint, choice
import sqlite3
from asyncio import TimeoutError

# Discord
import nextcord as discord
from nextcord.ext import commands

# Third Party
import aiosqlite
import ujson as json

# Local Code
from cogs.utils import embeds
from cogs.utils.custom_checks import WaitForChecks


class Economy(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.emoji = '🪙'
        self.desc = 'literally an economy system'

        self.notice_embeds = embeds.NoticeEmbeds(client=client)

    def create_profile(self, user_id):
        con = sqlite3.connect(self.client.db)
        cur = con.cursor()

        with con:
            cur.execute(
                'INSERT INTO economy VALUES (:id, :wallet, :bank, :items)',
                {'id': user_id, 'wallet': 200, 'bank': 50, 'items': None}
            )

            con.commit()

    @commands.command(aliases=["profile", "balance"], brief='Views your balance.')
    async def bal(self, ctx, user: discord.Member = None):
        if not user:
            user = ctx.author

        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT wallet, bank FROM economy WHERE id = :id", {'id': user.id}) as cur:
                profile = await cur.fetchone()

        if not profile:
            a = '\''
            await self.notice_embeds.error(
                ctx, "Error loading profile",
                f"{f'You don{a}t' if ctx.author.id == user.id else f'{user.name} doesn{a}t' } have a profile.")
            return self.create_profile(user.id)

        e = discord.Embed(
            title=f"Balance of {user.name}",
            color=discord.Color.green(),
            description='\n'.join([
                f"**Wallet:** {profile[0]} `∆`",
                f"**Bank:** {profile[1]} `∆`"
            ])
        )

        e.set_thumbnail(url=user.display_avatar.url)
        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief="Work and get some cash.")
    async def work(self, ctx):
        async with aiosqlite.connect(self.client.db) as db:
            async with await db.execute("SELECT wallet, bank FROM economy WHERE id = :id", {'id': ctx.author.id}) as \
                    cur:
                profile = await cur.fetchone()

            if not profile:
                await self.notice_embeds.error(ctx, "Error loading profile", "You don't have a profile.")
                return self.create_profile(ctx.author.id)

            strings = (
                (f"{ctx.author.name} washed the dishes and $CashState", randint(20, 45)),
                (f"{ctx.author.name} wrote a song for Hatsune Miku and $CashState", randint(230, 450))
            )

            rand = random.choice(strings)

            if rand[1] < 0:
                calculated = int(str(int(profile[1] - rand[1])))
                collection_status = 'lost'
            else:
                calculated = int(str(int(profile[1] + rand[1])))
                collection_status = 'earned'

            await ctx.reply(rand[0].replace('$CashState', f"{collection_status} {rand[1]} `∆`."), mention_author=False)

            await db.execute(
                "UPDATE economy SET bank = :calculated_earnings WHERE id = :id",
                {'id': ctx.author.id, 'calculated_earnings': calculated}
            )

            await db.commit()

    @commands.command(brief="Answer a few trivia questions and not win anything")
    async def trivia(self, ctx):
        with open(f"{self.client.json}/trivia.json") as trivia_json:
            trivia_questions = json.load(trivia_json)

        trivia_question = choice(trivia_questions)
        e = discord.Embed(
            title=trivia_question['question'],
            color=discord.Color.green(),
            description='\n'.join([
                f"A) **{trivia_question['answers']['a']}**",
                f"B) **{trivia_question['answers']['b']}**",
                f"C) **{trivia_question['answers']['c']}**",
                f"D) **{trivia_question['answers']['d']}**"
            ])
        )

        e.add_field(name="Difficulty", value=f"`{trivia_question['difficulty']}`")
        e.add_field(name="Category", value=f"`{trivia_question['category']}`")
        await ctx.reply(embed=e, mention_author=False)

        check = WaitForChecks(self.client, ctx)

        try:
            answer = await self.client.wait_for('message', check=check.aligned_ctx, timeout=15)

            if answer.content.upper() != trivia_question['correct']:
                await ctx.send("**You're wrong.** The correct answer is "
                               f'`{trivia_question["answers"][trivia_question["correct"].lower()]}`.')
            else:
                await ctx.send('right')
        except TimeoutError:
            return await ctx.send('no reply :pensive:')


def setup(client):
    client.add_cog(Economy(client))
