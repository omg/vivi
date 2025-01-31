import io
import datetime
import discord
from enum import Enum
from typing import Literal, List, Union
from typing_extensions import Self
from modules.errors import ProposalParsingError

class BaseProposal:
    def __init__(
        self,
        pid: str,
        forum_id: str,
        thread_id: str,
        title: str,
        patch: str | bytes | io.BufferedIOBase,
        author: str,
        timestamp: int = datetime.datetime.now()
    ):
        self.pid = pid
        self.forum_id = forum_id
        self.thread_id = thread_id
        
        self.title = title
        self.patch = patch
        self.author = author
        self.created_at = timestamp
        self._convert_patch_to_str()

    def _convert_patch_to_str(self) -> None:
        if isinstance(self.patch, bytes):
            self.patch = self.patch.decode("utf-16")
        elif not isinstance(self.patch, str):
            raise ValueError("Patch must be a string or bytes")
    
    def patch_to_file(self) -> io.BytesIO:
        return io.BytesIO(self.patch.encode("utf-16"))
    
    def patch_to_str(self) -> str:
        return self.patch
    
    @staticmethod
    async def from_database(proposal_id: str) -> Self:
        if (cached := Proposal.__get_cached(proposal_id=proposal_id)) != None:
            return cached
        
        # TODO: ask database for info :D
        pass

    @staticmethod
    async def __get_cached(**kwargs) -> Self | None:
        """
        Args
        ------
        thread_id: `str` the id of the thread the proposal is related to
        proposal_id: `str` the internal id of the proposal
        """

        return next(
            (p for p in PROPOSALS
                if p.thread_id == kwargs.pop("thread_id", None) or
                    p.proposal_id == kwargs.pop("proposal_id", None)
            ), None
        )

class ProposalAction:
    def __init__(
        self,

    ):
        pass

class Proposal(BaseProposal):
    def __init__(
        self,
        pid: str,
        forum_id: str,
        thread_id: str,
        title: str,
        patch: str | bytes | io.BufferedIOBase,
        author: str,
        log: List[ProposalAction] = [],
        timestamp: int = datetime.datetime.now()
    ):
        super().__init__(
            pid,
            forum_id,
            thread_id,
            title,
            patch,
            author,
            timestamp
        )
        self.log = log
        



# class ProposalActionLog:
#     def __init__(
#         self,
#         proposal_id: str,
#         action: Literal["edit", "fork", "approve", "reject", "archive"],
#         patch_content: str,

#         action_author: str,
#     ):
#         self.proposal_id = proposal_id
#         self.action = action
#         self.patch_content = patch_content

#         self.action_author = action_author
#         self.action_at = datetime.datetime.now()

#     @staticmethod
#     async def from_original_message(message: discord.Message) -> List["ProposalActionLog"]:
#         return []

#     @staticmethod
#     async def from_database(proposal_id: str) -> List["ProposalActionLog"]:
#         pass

# async def _grab_original_proposal(thread: discord.Thread) -> discord.Message:
#     # APPARENTLY. the original starting message of threads is the same id as the thread itself, which is interesting
#     # also thread.starter_message may not be cached, so we need to fetch it in some cases
#     # there is a get_partial_message, but as far as i could tell, it wont let us grab the file from the message
#     original_message = thread.starter_message if thread.starter_message else await thread.fetch_message(thread.id)

#     return original_message

# async def _parse_original_proposal(original: discord.Message) -> str:
#     if original.attachments:
#         if original.attachments[0].filename.endswith(".patch"):
#             return (await original.attachments[0].read()).decode()
#         else:
#             raise ProposalParsingError("The original proposal does not have a .patch file, but has an attachment.")

#     start = original.content.find("```diff")
#     if start == -1:
#         raise ProposalParsingError("The original proposal does not contain a diff code block.")
#     else:
#         start += 7
#         end = original.content.find("```", start)

#     return original.content[start:end]

# async def get_original_proposal(thread: discord.Thread) -> str:
#     original = await _grab_original_proposal(thread)
#     return await _parse_original_proposal(original)

# class Proposal:
#     def __init__(
#         self,
#         proposal_id: str,
#         thread_id: str,
#         title: str,
#         patch: str | bytes | io.BufferedIOBase,
#         author: str,
#         log: List[ProposalActionLog] = [],
#     ):
#         self.proposal_id = proposal_id
#         self.thread_id = thread_id
#         self.title = title
#         self.patch = patch
#         self._convert_patch_to_str()
#         self.log = log

#         self.author = author
#         self.created_at = datetime.datetime.now()

#     def _convert_patch_to_str(self) -> None:
#         if isinstance(self.patch, bytes):
#             self.patch = self.patch.decode("utf-16")
#         elif not isinstance(self.patch, str):
#             raise ValueError("Patch must be a string or bytes")

#     def patch_to_file(self) -> io.BytesIO:
#         return io.BytesIO(self.patch.encode("utf-16"))
    
#     def patch_to_str(self) -> str:
#         return self.patch

#     def remove(self, words: str) -> None:
#         lines = { k:v for k,v in enumerate(self.patch.split("\n")) }
#         for line_num, line in lines.items():
#             if any(word in line for word in words) and not line.startswith("#"):
#                 del lines[line_num]
        
#         self.patch = "\n".join(lines.values())

#     def add(self, additions: str) -> None:
#         self.patch += "\n\n" + additions
    
#     def edit(self, new_patch: str) -> None:
#         self.patch = new_patch

#     # def fork(self, words_to_fork: list[str]) -> 

#     def is_too_long(self) -> bool:
#         return len(self.patch) < 1500 and self.patch.count("\n") <= 100

#     @staticmethod
#     async def from_original_message(thread: discord.Thread) -> "Proposal":
#         if (cached := Proposal._get_cached(thread_id=thread.id)) is not None:
#             return cached
        
#         # BUG: this will error and break if the original message is deleted, hopefully that doesnt happen :D
#         op_message = await _grab_original_proposal(thread)
#         patch = await _parse_original_proposal(op_message)

#         prop = Proposal(
#             proposal_id = "temporary value",
#             thread_id = thread.id,
#             title = thread.name,
#             patch = patch,
#             author = "temporary value",
#             log = ProposalActionLog.from_original_message(op_message),
#         )

#         PROPOSALS.append(prop)

#         return prop

#     @staticmethod
#     async def from_database(proposal_id: str) -> "Proposal":
#         if (cached := Proposal._get_cached(proposal_id=proposal_id)) is not None:
#             return cached
        
#         pass

#     @staticmethod
#     def _get_cached(**kwargs) -> Union["Proposal", None]:
#         """
#         READ ME!!!!!!!!!!!!!!
        
#         Pass this function "thread_id=" or "proposal_id="
#         """
#         # python doesnt support overloading (Natively) but it might make sense to use both of these
#         return next((p for p in PROPOSALS if p.thread_id == kwargs.pop("thread_id", None) or p.proposal_id == kwargs.pop("proposal_id", None)), None)
    

# # in memory cache of the proposals as to not have unnecessary database calls
# # even though its not exactly an issue since proposals wont be made or updated that often
PROPOSALS: List[Proposal] = []