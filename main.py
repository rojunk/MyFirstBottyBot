import discord
import asyncio
from discord.ext import commands
import yt_dlp

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='!', intents=intents)

ffmpeg_options = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5 -re',
    'options': '-vn -bufsize 64k',
}

ydl_opts = {
    'format': 'bestaudio/best',
    'extractaudio': True,
    'audioquality': 1,
    'quiet': True,
}

@bot.command()
async def test(ctx):
    await ctx.send('TestyTestTest')

@bot.command()
async def play(ctx, *, query: str):
    if ctx.author.voice:
        channel = ctx.author.voice.channel
        if not ctx.voice_client:
            await channel.connect()
    else:
        await ctx.send("You must be in a voice channel to play music!")
        return

    if query.startswith("http"):
        if "soundcloud" in query:
            source_type = "SoundCloudDirect"
        else:
            source_type = "Direct"
    else:
        source_type = "YouTubeSearch"

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        if source_type == "Direct" or source_type == "SoundCloudDirect":
            info = ydl.extract_info(query, download=False)
        else:
            info = ydl.extract_info(f"ytsearch:{query}", download=False)['entries'][0]

        audio_formats = [f for f in info['formats'] if f.get('acodec') != 'none' and f.get('abr') is not None]

        if not audio_formats:
            await ctx.send("No suitable audio formats found.")
            return

        best_audio = max(audio_formats, key=lambda f: f['abr'])

        audio_url = best_audio['url']
        title = info.get('title')

    source = discord.FFmpegPCMAudio(audio_url, **ffmpeg_options)
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
    ctx.voice_client.play(source, after=lambda e: asyncio.run_coroutine_threadsafe(next_song(ctx), bot.loop) if e is None else print(f"Error: {e}"))
    await ctx.send(f'Now playing: **{title}**')

async def next_song(ctx):
    pass

@bot.command()
async def stop(ctx):
    if ctx.voice_client and ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send('**Music stopped!**')

bot.run('MTMxMzQ3MDQ5Mzk4NjI1ODk3NA.GlgLtK.bxzAOX20u0DmcnPqDfpQzHOlTLpJVGmZo4yyio')


