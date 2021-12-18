# StdLib
from os import getenv

# Discord
import nextcord as discord
from nextcord.ext import commands

# Third Party
from redditeasy import Subreddit, User

# Local Code
from cogs.utils import help, reddit, embeds


class Reddit(commands.Cog):
    def __init__(self, client):
        self.client = client
 
        self.emoji = '👽'
        self.desc = 'Commands that can display posts from subreddits'

        self.extras = {
            'reddit': {
                'examples': [
                    f"`{client.prefix}reddit softwaregore`",
                    f"`{client.prefix}reddit aww`"
                ]
            }
        }
        
        self.reddit_utils = reddit.RedditUtils(client=client)
        self.help_menus = help.HelpMenus(client)
        self.embed_notices = embeds.NoticeEmbeds(client)

    # Reddit
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Get a post from a subreddit or user of your choice.", usage="<subreddit>")
    async def reddit(self, ctx, subreddit: str):
        """
        Gets a post from a subreddit or user specified by the user.
        The r/ should not be added. Add u/ at the start to use the user as a source.

        **Notes**
        Video content will not render properly.
        """

        if subreddit.startswith("u/"):
          post = User(
                client_id=getenv("REDDIT_ID"),
                client_secret=getenv("REDDIT_TOKEN"),
                user_agent=getenv("REDDIT_STRING")
            )
          
          p = post.get_post(user=subreddit.replace("u/", ""))
        else:
            post = Subreddit(
                client_id=getenv("REDDIT_ID"),
                client_secret=getenv("REDDIT_TOKEN"),
                user_agent=getenv("REDDIT_STRING")
            )
          
            p = post.get_post(subreddit=subreddit.replace("r/", ""))
        
        is_nsfw = ctx.channel.is_nsfw() if ctx.guild is not None else False
        
        if not is_nsfw and p.nsfw:
          return await self.embed_notices.error(ctx, "This post was NSFW!", "You must be in an NSFW channel to view NSFW content")

        if p.is_media:
            e = discord.Embed(
                title=p.title,
                url=p.post_url,
                color=discord.Color.green(),
            )

            e.set_image(url=p.content)
        else:
            if p.content:
                if len(p.content) >= 4087:
                    split = [p.content[i:i + 4087] for i in range(0, len(p.content), 4087)]
                    content = f"{split[0]} `[CHAR]`"
                else:
                    content = p.content
            else:
                content = None

            e = discord.Embed(
                title=p.title,
                url=p.post_url,
                color=discord.Color.green(),
                description=content
            )

        e.set_footer(text=f"👤 {p.author} • 👍 {p.score} • 🥇 {p.total_awards} • 💬 {p.comment_count}")
        await ctx.reply(mention_author=False, embed=e)

    # H
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Get a post from r/TheLetterH.")
    async def h(self, ctx):
        await self.reddit_utils.post(ctx=ctx, subreddit="TheLetterH")

    # --------------------------------

    # Copypasta: Group
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.group(brief="Post a copypasta.")
    async def copypasta(self, ctx):
        if ctx.invoked_subcommand is None:
            await self.help_menus.menu(ctx, 'copypasta', ':scroll: Copypasta', 'Lorem ipsum dolor sit amet, '
                                                                               'consectetur adipiscing elit, '
                                                                               'sed do eiusmod tempor incididunt ut '
                                                                               'labore et dolore magna aliqua. '
                                                                               'Facilisis mauris sit amet massa '
                                                                               'vitae. Duis ut diam quam nulla '
                                                                               'porttitor. Risus in hendrerit gravida '
                                                                               'rutrum quisque. Ornare arcu dui '
                                                                               'vivamus arcu felis bibendum ut '
                                                                               'tristique. Nulla posuere sollicitudin '
                                                                               'aliquam ultrices sagittis orci a '
                                                                               'scelerisque. Felis bibendum ut '
                                                                               'tristique et egestas quis. Quis '
                                                                               'blandit turpis cursus in hac. Arcu '
                                                                               'cursus vitae congue mauris rhoncus '
                                                                               'aenean. Sit amet nulla facilisi morbi '
                                                                               'tempus iaculis urna id. Proin '
                                                                               'sagittis nisl rhoncus mattis rhoncus '
                                                                               'urna neque viverra justo. Nulla '
                                                                               'facilisi nullam vehicula ipsum a arcu '
                                                                               'cursus vitae congue. Eget nulla '
                                                                               'facilisi etiam dignissim diam quis. '
                                                                               'Sed nisi lacus sed viverra tellus in '
                                                                               'hac. Nec ullamcorper sit amet risus. '
                                                                               'Aliquet nec ullamcorper sit amet '
                                                                               'risus nullam eget felis. Consequat '
                                                                               'interdum varius sit amet mattis. '
                                                                               'Sociis natoque penatibus et magnis '
                                                                               'dis. Felis eget velit aliquet '
                                                                               'sagittis id consectetur. Egestas '
                                                                               'fringilla phasellus faucibus '
                                                                               'scelerisque eleifend donec pretium '
                                                                               'vulputate sapien. Dui ut ornare '
                                                                               'lectus sit amet. Nulla facilisi morbi '
                                                                               'tempus iaculis.')

    # Copypasta: Normal
    @copypasta.command(brief="Get a post from r/Copypasta.")
    async def normal(self, ctx):
        await self.reddit_utils.pasta(ctx=ctx, subreddit="Copypasta")

    # Copypasta: Emoji
    @copypasta.command(brief="Get a post from r/Emojipasta.")
    async def emoji(self, ctx):
        await self.reddit_utils.pasta(ctx=ctx, subreddit="Emojipasta")

    # --------------------------------

    # Cat
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Post cat pictures.")
    async def cat(self, ctx):
        options = ["cat", "catsareliquid", "cats", "catwallpapers", "blurrypicturesofcats", "60fpscats",
                   "SupermodelCats", "catpictures", "tightpussy"]

        await self.reddit_utils.multi_reddit(ctx=ctx, options=options)

    # Dog
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Post dog pictures.")
    async def dog(self, ctx):
        options = ["corgi", "puppies", "goldenretrievers", "dogpictures", "shiba", "rarepuppers"]

        await self.reddit_utils.multi_reddit(ctx=ctx, options=options)

    # Fox
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Post fox pictures.")
    async def fox(self, ctx):
        options = ["EverythingFoxes"]

        await self.reddit_utils.multi_reddit(ctx=ctx, options=options)

    # --------------------------------

    # Hmmm
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Get a post from r/Hmmm.")
    async def hmmm(self, ctx):
        await self.reddit_utils.post(ctx=ctx, subreddit="hmmm")

    # Me_IRL
    @commands.cooldown(1, 5, commands.BucketType.user)
    @commands.command(brief="Get a post from r/Me_IRL.")
    async def me_irl(self, ctx):
        await self.reddit_utils.post(ctx=ctx, subreddit="me_irl")


def setup(client):
    client.add_cog(Reddit(client))
