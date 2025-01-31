import re, random
import discord
from dotenv import dotenv_values
from datetime import datetime, timedelta
from modules.errors import ProposalParsingError

def is_older_than(time: datetime, diff_seconds: int) -> bool:
    return (datetime.now(time.tzinfo) - time) > timedelta(seconds=diff_seconds)

def random_base62() -> str:
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choice(digits) for _ in range(9))

def idify(uname: str, title: str) -> str:
    string = title.strip(" ")
    string = re.sub(r"([ -/])+", "-", string.lower()) #replace space - / with -
    string = re.sub(r"[^a-z0-9-]", "", string) #remove unapproved characters (for id)
    if len(string) > 20:
        string = "-".join(string.split("-")[:2])
        if len(string) > 20:
            string = string.split("-")[0][:20].strip("-")
    return f"{uname.lower()}-{string}-{random_base62()}"

def extract(text: str, prefix: str) -> str | None:
    pattern = fr"<!--{prefix} ([\w]+)-->"
    match = re.search(pattern, text)
    return match.group(1) if match else None

def remove_lines(text: str, words: list[str]) -> str:
    lines = text.split("\n")
    new_lines = [line for line in lines if not any(word in line for word in words)]
    return "\n".join(new_lines).strip()

def find_words_in_diff(text: str) -> list[str]:
    # return re.findall(r"^(\+ ?|- ?)\w+", text)
    return [re.sub(r'\+-', "", word).strip() for word in text.split('\n') if word.startswith("+") or word.startswith("-")]

def clean_proposal(text: str) -> str:
    return re.sub(r"[^ a-zA-Z0-9,.!?'\"\&\+\-\#\/\n]", "", text)

#Filter Strings
TITLE_FILTER = r"""[^ a-zA-Z0-9,.!?'":;\(\)\[\]-]"""
DESC_FILTER = r"""[^ a-zA-Z0-9,.!?'":;\(\)\[\]\$\%\&\+\=\|-]"""

env = dotenv_values()
GUILD = discord.Object(id = int(env["GUILD_ID"]))

