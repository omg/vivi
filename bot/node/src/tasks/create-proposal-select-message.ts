import { EmbedBuilder, TextChannel } from "discord.js";
import { vivi } from "../client";
import { getLanguageSelectComponent } from "../languages/getLanguageSelectComponent";
import { Languages } from "../languages/Languages";

const vivisLibrary = vivi.guilds.cache.get("916755802059055184")!;
const proposalMessageChannel = vivisLibrary.channels.cache.get(
  "1318302066287972372"
) as TextChannel;

const embed = new EmbedBuilder()
  .setTitle(`${Languages[0].translations.embed.title}`)
  .setDescription(
    Languages.map((language) => {
      return `- ${language.flag} **${language.translations.languageSelectString}**`;
    }).join("\n")
  )
  .setColor("#239be0");

proposalMessageChannel.send({
  embeds: [embed],
  components: getLanguageSelectComponent(
    "proposal-start",
    Languages[0].translations.languageSelectString
  ),
});
