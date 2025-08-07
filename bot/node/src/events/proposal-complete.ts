import { MessageFlags } from "discord.js";
import { vivi } from "../client";

vivi.on("interactionCreate", async (interaction) => {
  if (!interaction.isModalSubmit()) return;
  if (interaction.customId !== "proposal-complete") return;
  const patchString = interaction.fields.getTextInputValue("patch");
  console.log({ patchString });
  interaction.reply({
    flags: MessageFlags.Ephemeral,
    content: "Received submission.",
  });
});
