import {
  ActionRowBuilder,
  ModalBuilder,
  TextInputBuilder,
  TextInputStyle,
} from "discord.js";
import { vivi } from "../client";
import { getLanguage } from "../languages/Languages";
import { proposalInteractions } from "./proposal-start";

const dev = true;

const placeholder = `
# Comment
+ ADDITION
- REMOVAL
`;

const examplePatch = `
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
`;

const defaultValue = dev
  ? "This is currently in development and being tested. Do not actually send an actual submission right now! It won't be saved."
  : examplePatch;

vivi.on("interactionCreate", async (interaction) => {
  if (!interaction.isStringSelectMenu()) return;
  if (interaction.customId !== "proposal-select-start") return;

  const [selectedLanguageValue] = interaction.values;
  if (!selectedLanguageValue) return;
  const language = getLanguage(selectedLanguageValue);
  if (!language) return;

  const modal = new ModalBuilder()
    .setCustomId("proposal-complete")
    .setTitle("Create proposal");

  const patchInput = new TextInputBuilder()
    .setCustomId("patch")
    .setStyle(TextInputStyle.Paragraph)
    .setLabel("Patch file")
    .setPlaceholder(placeholder)
    .setValue(defaultValue + "\n\n" + language.localizedName)
    .setMinLength(4)
    .setRequired(true);

  const actionRow = new ActionRowBuilder<TextInputBuilder>().addComponents(
    patchInput
  );

  modal.addComponents(actionRow);

  await interaction.showModal(modal);

  const previousInteraction = proposalInteractions.get(interaction.user.id);
  if (previousInteraction && previousInteraction.replied) {
    try {
      await previousInteraction.deleteReply();
    } catch {}
  }
});
