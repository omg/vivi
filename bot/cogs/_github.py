import discord
import github as gh
from discord.ext import commands
from discord import app_commands
from dotenv import dotenv_values

env = dotenv_values()
# ghtoken = env["GITHUB_TOKEN"]

# repo_name = "vivi"
# base_repo_author = env["BASE_REPO"]
# head_repo_author = env["HEAD_REPO"]

# gh_api = gh.Github(auth=gh.Auth.Token(ghtoken))

# base_repo = gh_api.get_repo(f"{base_repo_author}/{repo_name}")
# head_repo = gh_api.get_repo(f"{head_repo_author}/{repo_name}")

class Github(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot

    # @app_commands.Group(name='propose', description="Make a proposal")


async def setup(bot):
    await bot.add_cog(Github(bot))