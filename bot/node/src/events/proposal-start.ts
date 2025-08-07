import {
  ActionRowBuilder,
  ModalBuilder,
  TextInputBuilder,
} from "@discordjs/builders";
import {
  ButtonBuilder,
  ButtonInteraction,
  ButtonStyle,
  CacheType,
  EmbedBuilder,
  MessageFlags,
  StringSelectMenuInteraction,
  TextInputStyle,
} from "discord.js";
import { vivi } from "../client";
import { getLanguageSelectComponent } from "../languages/getLanguageSelectComponent";
import { getLanguage, Languages } from "../languages/Languages";

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

export const proposalInteractions = new Map<
  string,
  StringSelectMenuInteraction<CacheType>
>();

vivi.on("interactionCreate", async (interaction) => {
  if (!interaction.isStringSelectMenu()) return;
  if (interaction.customId !== "proposal-start") return;

  // const modal = new ModalBuilder()
  //   .setCustomId("proposal-complete")
  //   .setTitle("Create proposal");

  // const patchInput = new TextInputBuilder()
  //   .setCustomId("patch")
  //   .setStyle(TextInputStyle.Paragraph)
  //   .setLabel("Patch file")
  //   .setPlaceholder(placeholder)
  //   .setValue(defaultValue)
  //   .setMinLength(4)
  //   .setRequired(true);

  // const actionRow = new ActionRowBuilder<TextInputBuilder>().addComponents(
  //   patchInput
  // );

  // modal.addComponents(actionRow);

  proposalInteractions.set(interaction.user.id, interaction);

  // await interaction.showModal(modal);
  // await interaction.reply({
  //   flags: MessageFlags.Ephemeral,
  //   content:
  //     "Please make sure you understand how to make a patch file before creating a proposal.",
  //   components: getLanguageSelectComponent(
  //     "proposal-select-start",
  //     "PLACEHOLDER"
  //   ),
  // });

  const [selectedLanguageValue] = interaction.values;
  if (!selectedLanguageValue) return;
  const language = getLanguage(selectedLanguageValue);
  if (!language) return;

  const embed = new EmbedBuilder()
    .setTitle(language.translations.embed.title)
    .setDescription(
      `${language.translations.embed.description}\n\`\`\`patch\n${language.translations.patchExample}\n\`\`\``
    )
    .setColor("#239be0");

  const createProposalButton = new ButtonBuilder()
    .setEmoji("📝")
    .setLabel(language.translations.createAProposalString)
    .setStyle(ButtonStyle.Primary)
    .setCustomId("proposal-start");
  const actionRow = new ActionRowBuilder()
    .setComponents(createProposalButton)
    .toJSON();

  await interaction.reply({
    flags: MessageFlags.Ephemeral,
    embeds: [embed],
    components: [actionRow],
  });

  await interaction.message.edit({
    components: getLanguageSelectComponent(
      "proposal-start",
      Languages[0].translations.languageSelectString
    ),
  });
});
