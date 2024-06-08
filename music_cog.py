import discord
from discord.ext import commands
import logging

logging.basicConfig(level=logging.INFO)

from yt_dlp import YoutubeDL

class music_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.isplaying = False
        self.ispaused = False
        self.music_queue = []
        self.YDL_options = {'format': 'bestaudio', 'noplaylist': True}
        self.FFMPEG_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn',
            'executable': "C:\\Users\\angel\\ffmpeg-2024-06-06-git-d55f5cba7b-full_build\\bin\\ffmpeg.exe"
        }
        self.vc = None

    def search_yt(self, item):
        with YoutubeDL(self.YDL_options) as ydl:
            try:
                info = ydl.extract_info(f"ytsearch:{item}", download=False)
                logging.info(f"Extracted Info: {info}")
                video_info = info['entries'][0]
                logging.info(f"Video Info: {video_info}")
                return {'source': video_info['url'], 'title': video_info['title']}
            except Exception as e:
                logging.error(f"Error searching YouTube: {e}")
                return False

    def play_next(self):
        if len(self.music_queue) > 0:
            self.isplaying = True
            m_url = self.music_queue[0][0]['source']
            self.music_queue.pop(0)
            try:
                logging.info(f"Playing next song: {m_url}")
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_options), after=lambda e: self.play_next())
            except Exception as e:
                logging.error(f"Error playing next song: {e}")
                self.play_next()
        else:
            self.isplaying = False

    async def play_music(self, ctx):
        if len(self.music_queue) > 0:
            self.isplaying = True
            m_url = self.music_queue[0][0]['source']
            logging.info(f"URL to play: {m_url}")
            if self.vc is None or not self.vc.is_connected():
                try:
                    self.vc = await self.music_queue[0][1].connect()
                except Exception as e:
                    await ctx.send("Not able to connect to the voice channel.")
                    logging.error(f"Error connecting to voice channel: {e}")
                    return
            else:
                await self.vc.move_to(self.music_queue[0][1])

            self.music_queue.pop(0)
            try:
                logging.info("Starting playback")
                self.vc.play(discord.FFmpegPCMAudio(m_url, **self.FFMPEG_options), after=lambda e: self.play_next())
            except Exception as e:
                await ctx.send("Error playing the audio.")
                logging.error(f"Error playing audio: {e}")
                self.isplaying = False
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

    @commands.command(name="leave", aliases=['exit', 'quit'], help="Leave the voice channel")
    async def leave(self, ctx):
        self.isplaying = False
        self.ispaused = False
        await self.vc.disconnect()
    
    @commands.command(name="queue", aliases=['q'], help="Queue ka kaam uk")
    async def queue(self, ctx):
        if self.music_queue:
            queue_info = ""
            for index, item in enumerate(self.music_queue):
                queue_info += f"{index + 1}. {item[0]['title']}\n"
            await ctx.send(f"**Uhura Show Queue:\n{queue_info}**")
        else:
            await ctx.send("Add music , kirk out")
            
    
    @commands.command(name="np",help="Song ur playing rn")
    async def now_playing(self,ctx,play):
        if self.isplaying and self.music_queue:
            await ctx.send(f"What did u expect?: {play}")
        else:
            await ctx.send("Play Something")
            
    #@commands.command(name="remove", aliases=['re'],help="Removes the song from the queue")
    #async def remove(self,ctx,queue):
        