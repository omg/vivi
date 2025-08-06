import discord
from discord.ext import commands
from dotenv import dotenv_values

env = dotenv_values()
JOHNATHAN_ID = int(env["JOHNATHAN_ROLE_ID"])

class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # on_raw_reaction_add and on_reaction_add are different, raw_reaction_add is for all reactions, reaction_add is only for cached messages
    @commands.Cog.listener("on_raw_reaction_add")
    @commands.bot_has_permissions(manage_messages=True)
    async def reaction_killer(self, payload: discord.RawReactionActionEvent):
        channel = self.bot.get_channel(payload.channel_id)
        
        if channel != None and channel.parent_id == 1318302463140564995:
            message = channel.get_partial_message(payload.message_id)
            
            if len([x for x in payload.member.roles if x.id == JOHNATHAN_ID]) == 0:
                await message.remove_reaction(payload.emoji, payload.member)

    @commands.command()
    @commands.is_owner()
    async def sync(self, ctx: commands.Context):
        await self.bot.tree.sync(guild=discord.Object(env["GUILD_ID"]))
        await ctx.send("Yup")


async def setup(bot):
    await bot.add_cog(Listeners(bot))