import sys
import traceback
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

    # @commands.Cog.listener()
    # async def on_command_error(self, ctx: commands.Context, error):
    #     if hasattr(ctx.command, "on_error"):
    #         # if the command has its own error handler, we dont want to overwrite it
    #         # nor do we want to handle it twice
    #         return
        
    #     cog = ctx.cog
    #     if cog:
    #         if cog._get_overridden_method(cog.cog_command_error) is not None:
    #             # if the COG has its own error handler, we dont want to overwrite it
    #             return
        
    #     ignored = (commands.CommandNotFound, commands.NoPrivateMessage)
    #     error = getattr(error, "original", error)

    #     if isinstance(error, ignored):
    #         return
        
    #     elif isinstance(error, ProposalBotError):
    #         msg = await ctx.send(error.message)
    #         await msg.delete(delay=15)


async def setup(bot):
    await bot.add_cog(CommandErrorHandler(bot))