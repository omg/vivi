import discord, os, re, random
import github as gh
from dotenv import load_dotenv
from discord import app_commands
from datetime import datetime, timedelta
from task_queue import TaskQueue
from typing import Optional
from validate_diff import validate_diff

# Load environment variables

load_dotenv()

server_id = os.getenv("SERVER_ID")
token = os.getenv("DISCORD_TOKEN")
ghtoken = os.getenv("GITHUB_TOKEN")

repo_name = "vivi"
base_repo_author = os.getenv("BASE_REPO")
head_repo_author = os.getenv("HEAD_REPO")

# Set up the GitHub API

gh_api = gh.Github(auth=gh.Auth.Token(ghtoken))

base_repo = gh_api.get_repo(f"{base_repo_author}/{repo_name}")
head_repo = gh_api.get_repo(f"{head_repo_author}/{repo_name}")

# Set up the Discord bot

DISCORD_SERVER = discord.Object(id = int(server_id))

intents = discord.Intents.default()
intents.members = True

class BotClient(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.sync = False
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        await self.wait_until_ready()
        if not self.sync:
            self.sync = True
            await self.tree.sync(guild=DISCORD_SERVER)
        print("Bot ready, listening for commands!")

client = BotClient()

# Task queue

task_queue = TaskQueue(task_delay=90)

# Utility

def is_older_than(time: datetime, diff_seconds):
    return (datetime.now(time.tzinfo) - time) > timedelta(seconds=diff_seconds)

def update_proposals():
    global proposals
    proposals = [pull for pull in base_repo.get_pulls(state="open")]

def random_base62():
    digits = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return ''.join(random.choice(digits) for _ in range(9))

def idify(uname, title):
    string = title.strip(" ")
    string = re.sub(r"([ -/])+", "-", string.lower()) #replace space - / with -
    string = re.sub(r"[^a-z0-9-]", "", string) #remove unapproved characters (for id)
    if len(string) > 20:
        string = "-".join(string.split("-")[:2])
        if len(string) > 20:
            string = string.split("-")[0][:20].strip("-")
    return f"{uname.lower()}-{string}-{random_base62()}"

def extract(text, prefix):
    pattern = fr"<!--{prefix} ([\w]+)-->"
    match = re.search(pattern, text)
    return match.group(1) if match else None

update_proposals()

#Filter Strings
TITLE_FILTER = r"""[^ a-zA-Z0-9,.!?'":;\(\)\[\]-]"""
DESC_FILTER = r"""[^ a-zA-Z0-9,.!?'":;\(\)\[\]\$\%\&\+\=\|-]"""
# Commands

proposalGroup = app_commands.Group(name="proposal", description="Make a proposal", guild_ids=[DISCORD_SERVER])

@proposalGroup.command(name="create", description="Create a new proposal")
async def propose_changes(inter: discord.Interaction, diff: discord.Attachment, title: Optional[str], description: Optional[str]):
    if not is_older_than(inter.user.created_at, 259_200): # 3 days
        await inter.response.send_message("Your account is too young, come back later", ephemeral=True)
        return
    
    valid, data = validate_diff((await diff.read()).decode("utf-8")) #Validate .diff

    if not valid:
        await inter.response.send_message(data, ephemeral=True)
        return

    if title:
        title = re.sub(TITLE_FILTER, "", title) #Filter out unapproved characters
    else:
        title = "Unnamed"
    id = idify(inter.user.name, title)
    if description:
        desc = re.sub(DESC_FILTER, "", description).replace("GH-", "G​H-")
    else:
        desc = ""
    
    current_time = datetime.now().timestamp()
    completion_time = current_time + task_queue.get_estimated_wait(1)
    await inter.response.send_message(f"Proposal creation pending..\nEstimated completion time: <t:{completion_time}:T>", ephemeral=False)
    
    task_queue.add(new_pull, title=title, id=id, desc=desc, author=inter.user, data=data, inter=inter)
    return

@proposalGroup.command(name="edit", description="Edit an existing proposal")
async def edit_proposal(inter: discord.Interaction, proposal: str, diff: discord.Attachment):
    if not is_older_than(inter.user.created_at, 259_200): # 3 days
        await inter.response.send_message("Your account is too young, come back later", ephemeral=True)
        return
    valid, data = validate_diff((await diff.read()).decode("utf-8")) #Validate .diff

    if not valid:
        await inter.response.send_message(data, ephemeral=True)
        return
    
    current_time = datetime.now().timestamp()
    completion_time = current_time + task_queue.get_estimated_wait(1)
    await inter.response.send_message(f"Proposal edit pending..\nEstimated completion time: <t:{completion_time}:T>", ephemeral=False)
    
    task_queue.add(edit_pull, proposal=proposal, data=data, inter=inter)
    return

@edit_proposal.autocomplete(name="proposal")
async def proposal_auto(inter: discord.Interaction, current: str):
    ret = []
    for prop in proposals:
        if prop.user.login != head_repo_author: continue
        uid = int(extract(prop.body, "by"))
        if inter.user.id != uid: continue
        if current and not current in f"{prop.title} #{prop.number}": continue
        ret.append(app_commands.Choice(name=f"{prop.title} #{prop.number}", value=prop.head.ref))
    return ret[:25]

client.tree.add_command(proposalGroup, guild=DISCORD_SERVER)

# Functions

def new_pull_body(desc, user, id):
    if desc:
        return f"proposed by {user.name}\n### Notes\n{desc}\n\n<!--by {user.id}-->\n<!--id {id}-->"
    else:
        return f"proposed by {user.name}\n\n<!--by {user.id}-->\n<!--id {id}-->"

async def new_pull(title: str, id: str, desc: str, author: discord.User, data: str, inter: discord.Interaction):
    # Create the branch
    head_repo.create_git_ref(
        f"refs/heads/{id}",
        head_repo.get_branch("master").commit.sha
    )

    # Create the diff file
    head_repo.create_file(
        path=f"changes/{id}.diff",
        message="Create .diff",
        content=data,
        branch=id
    ) 

    # Create the pull request
    pr = base_repo.create_pull(
        title=f"{title} • {author.name}",
        base="master",
        body=new_pull_body(desc, author, id),
        head=f"{head_repo_author}:{id}",
        maintainer_can_modify=True
    )

    update_proposals()
    
    # try editing the original message
    try:
        await inter.edit_original_message(content=f"[Your proposal]({pr.html_url}) was created!")
    except:
        # send a new message
        try:
            await inter.channel.send(f"{inter.user.mention} [Your proposal]({pr.html_url}) was created!");
        except:
            pass

async def edit_pull(proposal: str, data: str, inter: discord.Interaction):
    # Retrieve the diff file
    file = head_repo.get_contents(f"changes/{proposal}.diff", ref=proposal)

    # Update the diff file
    head_repo.update_file(
        path=file.path,
        message="Update .diff",
        content=data,
        branch=proposal,
        sha=file.sha
    )
    
    # Get the pull request
    pr = [pull for pull in base_repo.get_pulls(state="open") if pull.head.ref == proposal][0]
    
    if not pr:
        return
        
    # try editing the original message
    try:
        await inter.edit_original_message(content=f"[Your proposal]({pr.html_url}) was edited!")
    except:
        # send a new message
        try:
            await inter.channel.send(f"{inter.user.mention} [Your proposal]({pr.html_url}) was edited!");
        except:
            pass

client.run(token=token)
