import re
import string
from modules.errors import ProposalValidationError
from shared import ProposalType
from typing import Literal, Optional, Union, List
from enum import Enum

"""
    Process the input text and make sure it is valid to be used to MODIFY a proposal.

    Slightly different from validate_diff, this forces the text to have ONLY words
    split by newlines, without whitespace or -/+/# characters at the start of the line
    mainly used for the add/remove commands
"""

def _format_addition(
    s: str, 
) -> str:
    formatted = []

    for line in s.split("\n"):
        line = line.strip()
        if len(line) == 0:
            formatted += "\n"
            continue

        if not line.startswith(("#", "+")):
            continue
        
        formatted.append(line)
        
    return "\n".join(formatted)

def _format_removal(s: str) -> str:
    formatted = []

    for line in s.split("\n"):
        line = line.strip()
        if len(line) == 0:
            formatted += "\n"
            continue

        if not line.startswith(("#", "-")):
            continue

        formatted.append(line)

    return "\n".join(formatted)

def _format_edit(s: str) -> str:
    formatted = []

    for line in s.split("\n"):
        line = line.strip()
        if len(line) == 0:
            formatted += "\n"
            continue

        if not line.startswith(("#", "-", "+")):
            continue

        formatted.append(line)

    return "\n".join(formatted)

def _format_fork(s: str) -> str:
    formatted = []

    for line in s.split("\n"):
        line = line.strip()
        if len(line) == 0:
            formatted += "\n"
            continue

        if not line.startswith(("#")):
            if line.startswith(("+", "-")):
                # replace "+ ", "+", "- ", "-" with "" in forks, since forks will take the "state" of the proposed word with it when forked
                line = re.sub(r"(\+|\-) ?", "", line)
            else:
                continue

        formatted.append(line)

def _split_comment(line: str, limit) -> str:
    if len(line) > limit:
        split_point = None
        for i, x in enumerate(line[limit::-1], 0):
            if x in string.whitespace:
                split_point = limit - i
                break

        split_point = limit if not split_point else split_point

        first_part = line[:split_point].rstrip()
        remaining_part = line[split_point:].lstrip()
        return first_part + "\n# " + _split_comment(remaining_part)
    
    return line

def format_proposal(text: str, pType: ProposalType) -> str:
    match pType:
        case ProposalType.ADDITION:
            f = _format_addition
        case ProposalType.REMOVAL:
            f = _format_removal
        case ProposalType.FORK:
            f = _format_fork
        case ProposalType.EDIT:
            f = _format_edit
    
    t = f(text)
    edited = []

    for line in t:
        if line.startswith("#"):
            if len(line) > 40:
                edited.append(_split_comment(line, 40))


# class LineAction(Enum):
#     REMOVE = 1
#     IGNORE = 2

# class LineType(Enum):
#     UNKNOWN = 0
#     TEXT = 2
#     COMMENT = 3

# class Line:
#     def __init__(
#         self,
#         text,
#         *,
#         autofill: str
#     ) -> None:
#         self.text = text
#         self._autofill = autofill

#         self.linetype = self._classify_line()

#     def _classify_line(self) -> LineType:
#         match self.text.strip()[0]:
#             case "#":
#                 return LineType.COMMENT
#             case "+" | "-":
#                 return LineType.TEXT
#             case _:
#                 if self._autofill:
#                     self.text = self._autofill_text()

#                 return LineType.UNKNOWN
    
#     def _autofill_text(self) -> str:
#         return self._autofill + " " + self.text

#     def validate(self, whitelist: str) -> bool:
#         wl = {k:"" for k in whitelist}
#         for char in self.text:
#             if wl.get(char):
#                 continue
#             else:
#                 return False
        
#         return True
    
#     def validate_and_remove(self, whitelist: str) -> None:
#         wl = {k:"" for k in whitelist}
#         validated = ""
        
#         for char in self.text:
#             if wl.get(char):
#                 continue
#             else:
#                 validated += char
        
#         self.text = validated

    
# class ProposalInputFormatter:
#     def __init__(
#         self,
#         *,
#         comment_action: LineAction = LineAction.IGNORE,
#         comment_character_limit: int = 40,
#         text_character_limit: int = 35,
#         first_character_autofill: str = "",
#         error_action: LineAction = LineAction.REMOVE,
#     ):
#         self.comment_action = comment_action
#         self.comment_character_limit = comment_character_limit

#         self.text_whitelist = string.ascii_letters + string.whitespace + "+-#'\"",
#         self.text_space_limit = 2
#         self.text_character_limit = text_character_limit

#         self.first_character_autofill = first_character_autofill

#         self.error_action = error_action
#         self.unknown_linetype_action: LineAction = LineAction.AUTOFILL
    
#     @staticmethod
#     def _insert_at(text: str, position: int, new: str) -> str:
#         return text[:position] + new + text[position:]

#     def _split_comment(self, line: str) -> str:
#         if len(line) > self.comment_character_limit:
#             split_point = None
#             for i, x in enumerate(line[self.comment_character_limit::-1], 0):
#                 if x in string.whitespace:
#                     split_point = self.comment_character_limit - i
#                     break

#             split_point = self.comment_character_limit if not split_point else split_point

#             first_part = line[:split_point].rstrip()
#             remaining_part = line[split_point:].lstrip()
#             return first_part + "\n# " + self._split_comment(remaining_part)
        
#         return line

#     def _enforce_character_limit(self, line: Line) -> str:
#         if line.linetype == LineType.COMMENT:
#             return self._split_comment(line)
#         else:
#             is_too_long = len(line) > self.text_character_limit
#             if is_too_long:
#                 if self.error_action == LineAction.REMOVE:
#                     return ""
            
#             return line

#     def format(self, s: str) -> str:
#         final = ""

#         for l in s.split("\n"):
#             line = Line(l)
#             if self.error_action == LineAction.REMOVE:
#                 line.validate_and_remove(self.text_whitelist)

#             l_text = self._enforce_character_limit(line)

#             final += l_text




        


# def process_proposal_input(
#     text: str,
#     *,
#     allow_comments: bool = True,
#     text_whitelist: str = string.ascii_letters + " +-#",
#     comment_whitelist: str = string.printable,
#     first_character_whitelist: str = "+-#",
#     text_space_limit: int = 2,
#     remove_offending_line:  Union[bool, Literal["comment"]]
# ) -> str:
#     """
#         Processes input to filter out any unwanted text and keep a consistent proposal format

#         Parameters
#         ----------
#         `allow_comments`: true if comments are allowed in the input, false if they arent 
#         comments will be considered offending lines if this is false
        
#         ^NOTE^ if allow_comments is on, "#" is added to the `first_character_whitelist` parameter, if its off then "#" will be stripped from `first_character_whitelist`

#         `text_whitelist`: string of characters that are allowed, this whitelist is exclusively for NON COMMENT LINES, 
#         if a line contains a letter not included then it will be considered an offending line

#         `comment_whitelist`: same as text_whitelist except exlusively FOR comment lines
#         comments that dont fulfill this WILL NOT be considered offending, and will only have the extra characters stripped out for encoding reasons

#         `first_character_whitelist`: only for the first character of the line, should be used to make sure lines contain +/-/# at the start of them
#         lines that dont fulfill this will be considered offending lines

#         `text_space_limit`: the maximum number of space characters allowed in a TEXT line, this is used to filter out lines that may be full sentences or comments
#         that might not be marked correctly, or to filter out mistakes when creating proposals, lines that exceed this number will be considered offending lines

#         `remove_offending_line`: used to denote if you want offending lines removed (true), ignored (false), or commented ("comment")
#     """
#     lines = []
#     if allow_comments:
#         first_character_whitelist += "#"
#     else:
#         first_character_whitelist = first_character_whitelist.strip("#")

#     for line_number, line in enumerate(text.split('\n'), start=1):
#         is_offending_line = False
#         line_type = None
#         for char_pos, char in enumerate(line, start=1):
#             if char_pos == 1:
#                 if char not in first_character_whitelist:
#                     is_offending_line = True
#                     break

#                 if char == "#":
#                     line_type = "comment"
#                 elif char == "+":
#                     line_type = "addition"
#                 elif char == "-":
#                     line_type = "removal"

#             else:
#                 if line_type == "comment":
#                     if char not in comment_whitelist:
#                         is_offending_line = True
#                         break
            
                    

            
            

    
#         if is_offending_line:
#             if not remove_offending_line:
#                 # if remove_offending_line is false, fall through and add the line
#                 pass
#             elif isinstance(remove_offending_line, bool):
#                 # if remove_offending_line is NOT false and it is a bool, skip the current line and dont add it
#                 continue
#             else:
#                 # remove_offending_line is something else, and we assume its "comment", so we comment the line out and add it
#                 line = "# " + line
        
#         lines.append(line)

#     return "\n".join(lines)


# def process_input_general(text: str) -> str:
#     whitelist = string.ascii_letters + " +-#"

#     lines = []

#     for line_number, line in enumerate(text.split('\n'), start=1):
#         if line.startswith("#"):
#             lines.append(line)
#             continue

#         # TODO: It might make more sense to turn these into comments, but i think that will get ugly
#         # erroring is probably a better solution
#         if line.count(" ") > 1:
#             continue
#             # raise ProposalValidationError(f"Invalid syntax on line {line_number}. Only one space allowed.")

#         for char in line:
#             if char not in whitelist:
#                 raise ProposalValidationError(f"Invalid syntax on line {line_number}. Invalid character: {char}")

#         lines.append(line)
    
#     return "\n".join(lines)

# def process_input_additions(text: str) -> str:
#     text = process_input_general(text)

#     for line_number, line in enumerate(text.split('\n'), start=1):
#         if not (line.startswith("+") or line.startswith("-") or line.startswith("#")):
#             raise ProposalValidationError(f"Invalid syntax on line {line_number}. Must start with +, -, or #")

#     return text

# def process_input_removals(text: str) -> str:
#     text = process_input_general(text)

#     for line_number, line in enumerate(text.split('\n'), start=1):
#         # easier to remove when theres no +/- and shit infront of it
#         re.sub(r"^[+-]\s*", "", line)

#     return text

# # just an idea, not sure if it should be done yet
# def enforce_formatting_rules():
#     """
#     Enforces specific formatting rules for proposals, such as:
#         - Lines must be split by newlines
#         - Lines must start with "+", "-", or "#"
#         - Lines must not contain more than one space 
#             (can be changed in the future, but currently is just so people dont write sentences in comments)
#         - Lines must not contain any characters other than letters, spaces, and the characters "+-#"
#         - Comments must not span more than 100 characters
#             (just for readability, i choose this number arbitrarily)
#         - Additions and Removals should be split into separate groups if possible
#             (this is hard to enforce, but just for testing we can take all the comments above the word that arent
#             split by new lines)
#     """
#     pass