import discord, io
from discord.ext import commands
from discord import app_commands
from typing import Literal
from modules.utility import GUILD
from bot.modules._proposals import Proposal, PROPOSALS
from modules.errors import GeneralCommandError
from bot.modules._formatting import process_input_additions, process_input_removals, process_input_general
from modules.pageview import PageView


class ProposalButton(discord.ui.View):
    def __init__(self, *, timeout = None):
        super().__init__(timeout=timeout)

        # 1 use every 5 minutes should be more than fine, especially since proposals dont HAVE to be split up
        self.cooldown = commands.CooldownMapping.from_cooldown(1, 300, commands.BucketType.user)

    @discord.ui.button(label="Create a proposal", custom_id="create_proposal", style=discord.ButtonStyle.primary)
    async def create_proposal_callback(
        self, 
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):
        bucket = self.cooldown.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()
        if retry_after:
            return await interaction.response.send_message(f"Please wait {retry_after:.2f} more seconds before creating another proposal.", ephemeral=True)

        # TODO: Replace this with a .env value
        forum: discord.ForumChannel = await interaction.client.fetch_channel(1318302463140564995)

        await interaction.response.send_modal(ProposalCreationModal(forum=forum))

class BaseProposalModal(discord.ui.Modal):
    def __init__(
        self,
        forum: discord.ForumChannel,
        *, 
        title = ..., 
        timeout = None, 
        custom_id = ...
    ) -> None:
        self.forum = forum
        super().__init__(title=title, timeout=timeout, custom_id=custom_id)
    
    async def filter_input(self, text, mode: Literal["add", "remove", "fork", "edit"]):
        t = process_input_general(text)

        if mode == "add":
            return process_input_additions(t)


class ProposalCreationModal(BaseProposalModal):
    pass
    

class ProposalEditModal(BaseProposalModal):
    pass

# class ProposalModalBase(discord.ui.Modal):
#     def __init__(
#         self, 
#         forum: discord.ForumChannel,
#         topbartitle: str = "Proposal"
#     ):
#         self.forum = forum
#         super().__init__(title=topbartitle)
    
#     async def clean_input(self, text: str) -> str:
#         return process_input_general(text)
        

# class ProposalCreationModal(ProposalModalBase):
#     def __init__(self, forum: discord.ForumChannel, topbartitle = "Proposal Creation"):
#         super().__init__(forum, topbartitle)
    
#     creation_title = discord.ui.TextInput(
#         label="Title",
#         placeholder="Enter the title of your proposal",
#         style=discord.TextStyle.short,
#         min_length=1,
#         max_length=100
#     )
#     text = discord.ui.TextInput(
#         label="Text (.patch)",
#         placeholder="Enter the proposal text here, in the .patch format",
#         style=discord.TextStyle.paragraph,
#         min_length=1,
#         max_length=4000
#     )

#     async def on_submit(self, interaction: discord.Interaction):
#         filtered = await self.clean_input(self.text.value)

#         content = ""
#         if len(filtered) < 1500 and filtered.count("\n") <= 100:
#             content = f"\n\n```diff\n{filtered}```"

#         thread = await self.forum.create_thread(
#             name=self.creation_title.value,
#             content=f"Proposal by {interaction.user.mention}" + content,
#             file=discord.File(io.BytesIO(filtered.encode()), filename="proposal.patch") if len(content) == 0 else discord.utils.MISSING
#         )

#         PROPOSALS.append(await Proposal.from_original_message(thread))

#         await interaction.response.send_message(content=f"Proposal submitted! View it here <#{thread.thread.id}>", ephemeral=True)

# class ProposalUpdateModal(ProposalModalBase):
#     def __init__(
#         self, 
#         forum: discord.ForumChannel,
#         original_content: Proposal,
#         update_type: Literal["add", "fork", "remove", "edit"] = "edit",
#         topbartitle = "Proposal Update"
#     ):
#         super().__init__(forum, topbartitle)
#         self.update_type = update_type
#         self.original_proposal: Proposal = original_content

#         if self.update_type == "edit":
#             self.textbox.default = self.original_proposal.patch_to_str()

#     textbox = discord.ui.TextInput(
#         label="Enter changes",
#         style=discord.TextStyle.paragraph,
#         min_length=1,
#         max_length=4000,
#     )

#     async def on_submit(self, interaction: discord.Interaction):
#         filtered = await self.clean_input(self.textbox.value)

#         proposal = self.original_proposal

#         if self.update_type == "add":
#             proposal.add(filtered)
#         elif self.update_type == "remove":
#             proposal.remove(filtered)
#         elif self.update_type == "fork":
#             pass
#         else:
#             proposal.edit(filtered)

#         content = ""
#         if len(filtered) < 1500 and filtered.count("\n") <= 100:
#             content = f"\n\n```diff\n{filtered}```"

#         await interaction.response.send_message(
#             content=f"{interaction.user.mention} Updated the proposal! View revised proposal below{content}", 
#             file=discord.File(proposal.patch_to_file()) if len(content) == 0 else discord.utils.MISSING, 
#             ephemeral=False
#         )

class Proposals(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        # TODO: Change message_id to the actual message id, using the .env value MESSAGE_ID
        # also note, this is what keeps the button working after restarts without needing to remake the message
        # which also allows the button to be changed without needing to update anything (as long as the custom_id doesnt change)
        self.bot.add_view(ProposalButton(), message_id=1318623113050587188)

    # TODO:
    # this makes sense as a check and it can be used, only after error handling is added, since this requires a custom error handler
    # to respond after the check fails (aka raise a custom error and have the error handler respond because of it)
    def is_proposal_channel():
        def predicate(interaction: discord.Interaction) -> bool:
            if not (interaction.channel.type == discord.ChannelType.public_thread and interaction.channel.parent_id == 1318302463140564995):
                raise GeneralCommandError("This command can only be used in the proposals forum channels.")
            
            return True
        return app_commands.check(predicate)

    @commands.command(name="reload", hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        await self.bot.unload_extension(f"cogs.{extension}")
        await self.bot.load_extension(f"cogs.{extension}")
        await ctx.send(f"Reloaded {extension}")

    # @commands.command(name="test")
    # @commands.is_owner()
    # async def testtesttest(self, ctx: commands.Context):
    #     embeds = [
    #         discord.Embed(title="Test1", description="Test1"),
    #         discord.Embed(title="Test2", description="Test2"),
    #         discord.Embed(title="Test3", description="Test3"),
    #         discord.Embed(title="Test4", description="Test4"),
    #         discord.Embed(title="Test5", description="Test5"),
    #     ]

    #     PageView().start()

    @commands.command(name="create")
    @commands.is_owner()
    async def create_proposal_message(self, ctx: commands.Context):
        # embed = discord.Embed(
        #     title="Understanding patch files",
        #     description="Making contributions to the dictionary is done by making a .patch file.\nPatch files describe how to modify the dictionary, by adding or removing words. It also supports comments. See the example below!\n\n```diff\n# Use comments to explain your changes.\n# Or use comments to create sections.\n\n+ ADD WORDS LIKE THIS\n+ ADD ANOTHER WORD\n+ USE CAPITAL LETTERS\n\n- REMOVE WORDS LIKE THIS\n- REMOVE ANOTHER\n- AND ANOTHER!\n\n# You can make comments anywhere\n\n- AND MAKE REMOVALS\n+ AND ADDITIONS\n- IN ANY ORDER```",
        #     color=0x2380eb
        # )
        # # channel = self.bot.get_channel(int(channelid))
        # await ctx.send(content="Start a proposal by pushing the button below.", embed=embed, view=ProposalButton())
        pass

    @app_commands.command(name="add")
    @app_commands.guilds(GUILD)
    @is_proposal_channel()
    async def add_to_proposal(
        self, 
        interaction: discord.Interaction,
    ):
        orig = await Proposal.from_original_message(interaction.channel)

        await interaction.response.send_modal(ProposalUpdateModal(
            forum=interaction.channel.parent,
            original_content=orig,
            update_type="add"
        ))
    
    @app_commands.command(name="remove")
    @app_commands.guilds(GUILD)
    @is_proposal_channel()
    async def remove_from_proposal(
        self,
        interaction: discord.Interaction
    ):
        orig = await Proposal.from_original_message(interaction.channel)

        await interaction.response.send_modal(ProposalUpdateModal(
            forum=interaction.channel.parent,
            original_content=orig,
            update_type="remove"
        ))

    @app_commands.command(name="edit")
    @app_commands.guilds(GUILD)
    @is_proposal_channel()
    async def edit_proposal(self, interaction: discord.Interaction, page: app_commands.Range[int, 1, 99] = 1):
        # if interaction.channel.type != discord.ChannelType.public_thread or interaction.channel.parent_id != 1318302463140564995:
        #     return await interaction.response.send_message("This command can only be used in the proposals forum channels.", ephemeral=True)

        # orig = await Proposal.from_original_message(interaction.channel)

        # await interaction.response.send_modal(ProposalUpdateModal(
        #     forum=interaction.channel.parent,
        #     original_content=orig,
        #     update_type="edit"
        # ))

        embeds = [
            discord.Embed(title="Test1", description="Test1"),
            discord.Embed(title="Test2", description="Test2"),
            discord.Embed(title="Test3", description="Test3"),
            discord.Embed(title="Test4", description="Test4"),
            discord.Embed(title="Test5", description="Test5"),
        ]

        await PageView().start(interaction, pages=embeds)

    # @app_commands.command(name="fork")
    # @app_commands.guilds(GUILD)
    # @is_proposal_channel()
    # async def fork_proposal(self, interaction: discord.Interaction):
    #     pass
        


async def setup(bot):
    await bot.add_cog(Proposals(bot))