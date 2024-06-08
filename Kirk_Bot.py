import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
from music_cog import music_cog

# Call load_dotenv() as a function
load_dotenv()

# Define intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.voice_states = True
intents.message_content = True 

# Create the bot with the defined intents
bot = commands.Bot(command_prefix="?", intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Add the music_cog as a cog
    await bot.add_cog(music_cog(bot))

# Run the bot using the token from environment variables
bot.run("MTI0ODE1MTMzMzk5NTgxMDg4OQ.GP_lBU.rRl7V-kPfrELlhOXC7J1PoA7zLs-I4Has-EoOs")