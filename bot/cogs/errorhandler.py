import discord
from discord.ext import commands

from modules.errors import ProposalBotError

class CommandErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.bot.tree.error = self.on_app_command_error

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: discord.app_commands.AppCommandError
    ):
        if isinstance(error, discord.app_commands.CommandInvokeError):
            error = error.original
            if isinstance(error, ProposalBotError):
                await interaction.response.send_message(error.message, ephemeral=True)
                return
            
        await interaction.response.send_message(str(error), ephemeral=True)

async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))