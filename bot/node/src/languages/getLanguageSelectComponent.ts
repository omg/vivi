import {
  ActionRowBuilder,
  StringSelectMenuBuilder,
  StringSelectMenuOptionBuilder,
} from "discord.js";
import { Languages } from "./Languages";

export function getLanguageSelectComponent(
  customId: string,
  placeholder: string
) {
  const dictionaryPicker = new StringSelectMenuBuilder()
    .setCustomId(customId)
    .setPlaceholder(placeholder)
    .setOptions(
      Languages.map((language) => {
        return new StringSelectMenuOptionBuilder()
          .setEmoji(language.flag)
          .setValue(language.value)
          .setLabel(language.localizedName)
          .setDescription(language.englishName);
      })
    );

  const actionRow = new ActionRowBuilder()
    .setComponents(dictionaryPicker)
    .toJSON();

  return [actionRow];
}
