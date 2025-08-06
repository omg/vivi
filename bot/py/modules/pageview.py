# this is a rewrite of a gist i found a long time ago for a paged embed,
# i made a few changes so it works with slash commands, and added some of my own things
# i forgot who the gist was from and couldnt find it when i went looking so unfortunately i cannot link or credit the original

import discord
import random
from discord.ext import commands
from discord.ui import Button, View
from typing import List, Callable, Optional

FIRST_EMOJI = "\u23EE"  # :track_previous:
LEFT_EMOJI = "\u2B05"  # :arrow_left:
RIGHT_EMOJI = "\u27A1"  # :arrow_right:
LAST_EMOJI = "\u23ED"  # :track_next:
DELETE_EMOJI = "\uFE0F"  # :wastebasket:
PAGINATION_EMOJIS = (FIRST_EMOJI, LEFT_EMOJI, RIGHT_EMOJI, LAST_EMOJI, DELETE_EMOJI)

class CustomButton:
    def __init__(
        self,
        action: Callable[["PageView"], int], # def func(pv: PageView) -> NewPage: int
        text: Optional[str] = "",
        emoji: Optional[str] = "",
    ) -> None:
        if not (text and emoji):
            raise TypeError("CustomButton requires a `text` or `emoji` parameter.")
        self.text = text
        self.emoji = emoji
        self.action = action
    
(
    FIRST_BUTTON,
    PREV_BUTTON,
    NEXT_BUTTON,
    LAST_BUTTON
) = (
    CustomButton(lambda pv: 1, emoji=FIRST_EMOJI),
    CustomButton(lambda pv: pv.curPage - 1 if pv.curPage != 1 else pv.totalPages, emoji=LEFT_EMOJI),
    CustomButton(lambda pv: pv.curPage + 1 if pv.curPage < pv.totalPages else 1, emoji=RIGHT_EMOJI),
    CustomButton(lambda pv: pv.totalPages, emoji=LAST_EMOJI)
)

class PageView(discord.ui.View):
    def __init__(self, *, 
        timeout = 180,
        row: List[CustomButton] = [FIRST_BUTTON, PREV_BUTTON, NEXT_BUTTON, LAST_BUTTON],
        initialpage: int = 1,
        ephemeral: bool = False
    ) -> None:
        self.row = row
        self.initialpage = initialpage
        self.ephemeral = ephemeral

        self.pages = None
        self.curPage = None
        self.totalPages = None
        self.interaction = None
        
        super().__init__(timeout=timeout)

    async def on_timeout(self):
        self.clear_items()
        await self.interaction.edit_original_response(
            embed=self.pages[self.curPage - 1], view=self
        )

        super().stop()
    
    async def _as_callback(self, _call: Callable[["PageView"], int]):
        async def _inner(interaction: discord.Interaction):
            self.curPage = _call(self)

            await self._edit()
            await interaction.response.defer()
        
        return _inner

    async def start(
        self, 
        interaction: discord.Interaction,
        pages: List[discord.Embed]
    ) -> None:
        self.pages = pages
        self.totalPages = len(pages)
        self.interaction = interaction
        self.curPage = self.initialpage

        for button in self.row:
            d_button = Button(label=button.text.format(**self.__dict__), emoji=button.emoji)
            d_button._super_secret_text_label = button.text
            d_button.callback = await self._as_callback(button.action)

            self.add_item(d_button)
        
        await self.interaction.response.send_message(
            embed=self.pages[self.curPage - 1], view=self, ephemeral=self.ephemeral
        )

    def _update_labels(self):
        for b in self.children:
            b.label = b._super_secret_text_label.format(**self.__dict__)

    async def _edit(self):
        self._update_labels()

        await self.interaction.edit_original_response(
            embed=self.pages[self.curPage - 1], view=self
        )

class PageCounter(discord.ui.Button):
    def __init__(self, style: discord.ButtonStyle, TotalPages, InitialPage):
        super().__init__(
            label=f"{InitialPage + 1}/{TotalPages}", style=style, disabled=True
        )
