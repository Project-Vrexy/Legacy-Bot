# StdLib
import re

# Discord
import nextcord as discord
from nextcord.ext import commands
import DiscordUtils

# Local Code
from cogs.utils import embeds, help
from cogs.utils.paginator import Paginator


class Music(commands.Cog):
    def __init__(self, client):
        self.client = client

        self.emoji = '🎵'
        self.desc = 'Commands that\'ll drop you to the beat'

        self.music = DiscordUtils.Music()

        self.notice_embeds = embeds.NoticeEmbeds(client)
        self.help_utils = help.HelpUtils(client)

    @commands.guild_only()
    @commands.command(aliases=["connect"], brief='Joins the voice channel')
    async def join(self, ctx):
        if ctx.author.voice is None:
            return await self.notice_embeds.error(ctx, "Error Joining", "You must be in a voice channel.")

        await ctx.author.voice.channel.connect()

        e = discord.Embed(
            title=":headphones: RIP HEADPHONE USERS",
            description=f"Connected to <#{ctx.author.voice.channel.id}>",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(aliases=["disconnect"], brief='Leaves the voice channel')
    async def leave(self, ctx):
        if ctx.author.voice is None:
            return await self.notice_embeds.error(ctx, "Error Leaving", "You must be in a voice channel.")

        e = discord.Embed(
            title=":headphones: NO WORRIES HEADPHONE USERS",
            description=f"Disconnected from <#{ctx.author.voice.channel.id}>",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)
        await ctx.voice_client.disconnect()

    @commands.command(brief='Adds a song to the queue.')
    async def play(self, ctx, *, url):
        player = self.music.get_player(guild_id=ctx.guild.id)
        if not player:
            try:
                player = self.music.create_player(ctx, ffmpeg_error_betterfix=True)
            except DiscordUtils.NotConnectedToVoice:
                return await self.notice_embeds.error(ctx, "Error Playing", "I am not in a voice channel!")

        if not ctx.voice_client.is_playing():
            try:
                await player.queue(url, search=True)
                song = await player.play()
            except (IndexError, TypeError):
                return await self.notice_embeds.error(ctx, "Error Playing", "No songs were found for your query.")

            e = discord.Embed(
                title=":play_pause: Now Playing!",
                description=f"[{song.name}]({song.url})",
                color=discord.Color.green()
            )
        else:
            try:
                song = await player.queue(url, search=True)
            except (IndexError, TypeError):
                return await self.notice_embeds.error(ctx, "Error Playing", "No songs were found for your query.")

            e = discord.Embed(
                title=":play_pause: Added to Queue!",
                description=f"[{song.name}]({song.url})",
                color=discord.Color.green()
            )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Pauses song playback.')
    async def pause(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.pause()

        e = discord.Embed(
            title=":pause_button: Paused",
            description=f"[{song.name}]({song.url})",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Resumes song playback.')
    async def resume(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.resume()

        e = discord.Embed(
            title=":arrow_forward: Resumed",
            description=f"[{song.name}]({song.url})",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Ends the current music session')
    async def stop(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        await player.stop()

        e = discord.Embed(
            title=":stop_button: Stopped",
            description="No songs in queue will be played.",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Sets the loop for the currently playing song')
    async def loop(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.toggle_song_loop()

        status = "Enabled" if song.is_looping else "Disabled"

        e = discord.Embed(
            title=f":repeat: {status} Looping",
            description=f"[{song.name}]({song.url})",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=None)

    @commands.command(brief='View the queue.')
    async def queue(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)

        pages = []

        extracted_songs = [
            f"{song_count}. [{song.name}]({song.url})"
            for song_count, song in enumerate(player.current_queue(), start=1)
        ]

        extracted_songs.sort(key=lambda x: int(x.split(" ")[0].replace(".", "")))
        split_songs = await self.help_utils.page_split(extracted_songs, 9)

        for i in range(len(split_songs)):
            song_chunks = split_songs[i]

            e = discord.Embed(
                title=f":musical_note: Queue for {ctx.guild.name}",
                description='\n'.join(song_chunks),
                color=discord.Color.green()
            )

            e.set_footer(text=f"Page {i + 1}/{len(split_songs)}")
            pages.append(e)
        try:    
            paginator = Paginator(self.client, ctx, pages)
            await paginator.run()
        except IndexError:
            return await self.notice_embeds.error(ctx, "Error Viewing Queue", "There are no songs in the queue.")

    @commands.command(brief='View the currently playing song.')
    async def np(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = player.now_playing()

        e = discord.Embed(
            title=":musical_note: Now Playing",
            description=f"[{song.name}]({song.url})",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Skip the currently playing song.')
    async def skip(self, ctx):
        player = self.music.get_player(guild_id=ctx.guild.id)
        data = await player.skip(force=True)
        queue = player.current_queue()
        if len(data) == 2:
            e = discord.Embed(
                title=":track_next: Skipped",
                color=discord.Color.green()
            )

            song = player.now_playing()
            e.add_field(name="Skipped Song", value=f"[{song.name}]({song.url})", inline=False)
            try:
                e.add_field(name="Now Playing Song", value=f"[{queue[queue.index(song)+1].name}]"
                                                           f"({queue[queue.index(song)+1].url})", inline=False)
            except IndexError:
                pass
        else:
            e = discord.Embed(
                title=":track_next: Skipped",
                description=f"[{data[0].name}]({data[0].url})",
                color=discord.Color.green()
            )
            await ctx.reply(embed=e, mention_author=False)
        await ctx.reply(embed=e, mention_author=False)    

    @commands.command(brief='Set the volume for the current song', usage='<vol>')
    async def volume(self, ctx, vol):
        if vol.lower() == "max":
            vol = 100
        elif vol.lower() == "min":
            vol = 5

        vol = re.sub(r"\.(?![0-9])", "", vol)

        if vol == "":
            return await self.notice_embeds.error(ctx, "Error Setting Volume", "That is not a number")

        if vol == 0:
            return await ctx.invoke(self.client.get_command("pause"))

        if vol in [1, 2, 3, 4]:
            vol = 5

        player = self.music.get_player(guild_id=ctx.guild.id)
        try:
            song, volume = await player.change_volume(float(vol) / 100)  # volume should be a float between 0 to 1
        except AttributeError:
            return await self.notice_embeds.error(ctx, "Error Setting Volume", "There is no song playing.")

        e = discord.Embed(
            title=f":speaker: Changed Volume to `{vol}`%",
            description=f"[{song.name}]({song.url})",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)

    @commands.command(brief='Remove a song from the queue', usage='<index>')
    async def remove(self, ctx, index: int):
        player = self.music.get_player(guild_id=ctx.guild.id)
        song = await player.remove_from_queue(int(index) - 1)

        e = discord.Embed(
            title=":track_next: Removed",
            description=f"[{song.name}]({song.url})",
            color=discord.Color.green()
        )

        await ctx.reply(embed=e, mention_author=False)


def setup(client):
    client.add_cog(Music(client))
