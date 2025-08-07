import { Client, IntentsBitField } from "discord.js";
import dotenv from "dotenv-multi-x";

dotenv.init();

const client = new Client({
  intents: [
    IntentsBitField.Flags.Guilds,
    IntentsBitField.Flags.GuildMembers,
    IntentsBitField.Flags.MessageContent,
    IntentsBitField.Flags.GuildMessageReactions,
    IntentsBitField.Flags.GuildMessages,
  ],
  allowedMentions: {
    parse: [],
  },
});

async function login(token: string): Promise<Client<boolean>> {
  return new Promise((resolve) => {
    client.login(token);
    client.on("ready", () => {
      console.log(`[bot] Logged in as ${client.user?.tag}`);
      resolve(client);
    });
  });
}

export const vivi = await login(process.env.VIVI_TOKEN!);
