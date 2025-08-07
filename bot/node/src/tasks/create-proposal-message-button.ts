import {
  ActionRowBuilder,
  ButtonBuilder,
  ButtonStyle,
  EmbedBuilder,
  TextChannel,
} from "discord.js";
import { vivi } from "../client";

const vivisLibrary = vivi.guilds.cache.get("916755802059055184")!;
const proposalMessageChannel = vivisLibrary.channels.cache.get(
  "1318302066287972372"
) as TextChannel;

const embed = new EmbedBuilder()
  .setTitle("Contributing to Vivi dictionaries")
  .setDescription(
    `
We're welcoming contributions from the community to improve Vivi! If you have new words to add to one of our dictionaries, or have any corrections you'd like to make, you can start a proposal by pressing the button below.
### Warning
<:Warning:1333998634752151674> **Your proposal must follow the \`.patch\` file format below.**
### Creating a proposal
Proposals are centered around \`.patch\` files. View the example file below to see how to structure your proposal.
### Example
\`\`\`patch
# Use comments to explain your changes.
# Or use comments to create sections.

+ ADD A WORD LIKE THIS
+ ADD ANOTHER WORD
+ USE CAPITAL LETTERS
- REMOVE WORDS LIKE THIS
- REMOVE ANOTHER
- AND ANOTHER!

# You can make comments anywhere

- AND MAKE REMOVALS
+ AND ADDITIONS
- IN ANY ORDER
\`\`\`
    `
  )
  .setColor("#239be0");

const createProposalButton = new ButtonBuilder()
  .setEmoji("📝")
  .setLabel("Create a proposal")
  .setStyle(ButtonStyle.Primary)
  .setCustomId("proposal-start");
const actionRow = new ActionRowBuilder()
  .setComponents(createProposalButton)
  .toJSON();

proposalMessageChannel.send({
  embeds: [embed],
  components: [actionRow],
});
