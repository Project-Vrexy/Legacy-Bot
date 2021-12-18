# StdLib
from os import getenv
from random import choice

# Discord
import nextcord as discord

# Third Party
from redditeasy import Subreddit


class RedditUtils:
    def __init__(self, client):
        self.client = client

    # Multi Reddit
    @staticmethod
    async def multi_reddit(ctx, options):
        s = choice(options)

        post = Subreddit(
            client_id=getenv("REDDIT_ID"),
            client_secret=getenv("REDDIT_TOKEN"),
            user_agent=getenv("REDDIT_STRING")
        )

        while True:
            p = post.get_post(subreddit=s)

            if p.is_media and len(p.title) <= 256 and p.nsfw is False:
                e = discord.Embed(
                    title=p.title,
                    url=p.post_url,
                    color=discord.Color.green()
                )

                e.add_field(name="👽 Subreddit", value=s)
                e.add_field(name="👤 Author", value=p.author, inline=False)

                e.set_footer(text=f"👍 {p.score} • 🥇 {p.total_awards} • 💬 {p.comment_count}")

                e.set_image(url=p.content)
                await ctx.reply(mention_author=False, embed=e)
                break

    # NSFW
    @staticmethod
    async def nsfw(ctx, options):
        s = choice(options)

        post = Subreddit(
            client_id=getenv("REDDIT_ID"),
            client_secret=getenv("REDDIT_TOKEN"),
            user_agent=getenv("REDDIT_STRING")
        )

        while True:
            p = post.get_post(subreddit=s)

            if p.is_media and len(p.title) <= 256:
                e = discord.Embed(
                    title=p.title,
                    url=p.post_url,
                    color=discord.Color.green()
                )

                e.add_field(name="👽 Subreddit", value=s)
                e.add_field(name="👤 Author", value=p.author, inline=False)

                e.set_footer(text=f"👍 {p.score} • 🥇 {p.total_awards} • 💬 {p.comment_count}")

                e.set_image(url=p.content)
                await ctx.reply(mention_author=False, embed=e)
                break

    # Pasta
    @staticmethod
    async def pasta(ctx, subreddit):
        post = Subreddit(
            client_id=getenv("REDDIT_ID"),
            client_secret=getenv("REDDIT_TOKEN"),
            user_agent=getenv("REDDIT_STRING")
        )

        while True:
            p = post.get_post(subreddit=subreddit)

            if not p.is_media and len(p.title) <= 256 and p.nsfw is False:
                if len(p.content) >= 4087:
                    split = [p.content[i:i + 4087] for i in range(0, len(p.content), 4087)]
                    content = f"{split[0]} `[CHAR]`"
                else:
                    content = p.content
                e = discord.Embed(
                    title=p.title,
                    description=content,
                    url=p.post_url,
                    color=discord.Color.green(),
                )

                e.set_footer(text=f"👤 {p.author} • 👍 {p.score} • 🥇 {p.total_awards} • 💬 {p.comment_count}")
                await ctx.reply(mention_author=False, embed=e)
                break

    # Post
    @staticmethod
    async def post(ctx, subreddit):
        post = Subreddit(
            client_id=getenv("REDDIT_ID"),
            client_secret=getenv("REDDIT_TOKEN"),
            user_agent=getenv("REDDIT_STRING")
        )

        while True:
            p = post.get_post(subreddit=subreddit)

            if p.is_media and len(p.title) <= 256 and p.nsfw is False:
                e = discord.Embed(
                    title=p.title,
                    url=p.post_url,
                    color=discord.Color.green(),
                )

                e.set_footer(text=f"👤 {p.author} • 👍 {p.score} • 🥇 {p.total_awards} • 💬 {p.comment_count}")
                e.set_image(url=p.content)

                await ctx.reply(mention_author=False, embed=e)
                break
