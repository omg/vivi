import discord
from discord.ext import commands
from dotenv import dotenv_values

env = dotenv_values()

class Editing(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot


async def setup(bot):
    await bot.add_cog(Editing(bot))