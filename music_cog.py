import discord
from discord.ext import commands

from yt_dlp import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.isplaying = False
        self.ispaused = False
        self.music_queue = []
        self.YDL_options = {'format': 'bestaudio', 'noplaylist': True}
        self.FFMPEG_options = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
                                'options': '-vn', 'executable':'C:\\Users\\angel\\ffmpeg-2024-06-03-git-77ad449911-full_build\\ffmpeg-2024-06-03-git-77ad449911-full_build\\bin'}
        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_options) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)['entries'][0]
            except Exception as e:
                print(f"Error searching YouTube: {e}")
                return False
            return {'source': info['formats'][0]['url'], 'title': info['title']}

    def play_next(self):
        if len(self.music_queue) > 0:
            self.isplaying = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url), after=lambda e: self.play_next())
        else:
            self.isplaying = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.isplaying = True
            m_url = self.music_queue[0][0]['source']
            if self.vc is None or not self.vc.is_connected():
                try:
                    self.vc = await self.music_queue[0][1].connect()
                except Exception as e:
                    await ctx.send("Not able to connect to the voice channel.")
                    print(f"Error connecting to voice channel: {e}")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_options), after=lambda e: self.play_next())
        else:
            self.isplaying = False

    @commands.command(name="play", aliases=['p', 'playing', 'P'], help="Play music")
    async def play(self, ctx, *args):
        query = " ".join(args)
        voice_channel = ctx.author.voice.channel
        if voice_channel is None:
            await ctx.send("Connect to a voice channel first.")
        elif self.ispaused:
            self.vc.resume()
        else:
            song = self.search_yt(query)
            if not song:
                await ctx.send("Couldn't find the requested song.")
            else:
                await ctx.send(f"Added {song['title']} to the queue.")
                self.music_queue.append([song, voice_channel])
                if not self.isplaying:
                    await self.play_music(ctx)

    @commands.command(name="pause", aliases=['pa'], help="Pause music")
    async def pause(self, ctx):
        if self.isplaying:
            self.isplaying = False
            self.ispaused = True
            self.vc.pause()
        elif self.ispaused:
            self.isplaying = True
            self.ispaused = False
            self.vc.resume()

    @commands.command(name="resume", aliases=['r', 'R'], help="Resume music")
    async def resume(self, ctx):
        if self.ispaused:
            self.isplaying = True
            self.ispaused = False
            self.vc.resume()

    @commands.command(name="skip", aliases=['s', 'Skip'], help="Skip music")
    async def skip(self, ctx):
        if self.vc and self.vc.is_playing():
            self.vc.stop()
            await self.play_music(ctx)

    @commands.command(name="leave", aliases=['exit', 'q', 'quit'], help="Leave the voice channel")
    async def leave(self, ctx):
        self.isplaying = False
        self.ispaused = False
        await self.vc.disconnect()