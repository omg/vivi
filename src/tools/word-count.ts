import appRootPath from "app-root-path";
import { readFile } from "fs/promises";

const args = process.argv.slice(2);

if (args.length !== 1) {
  console.error("Usage: tsx word-count <path from src>");
  process.exit(1);
}

let path = args[0];

const hasEnding = path.match(/\..+$/) !== null;
if (!hasEnding) {
  path = path + ".txt";
}

path = appRootPath.resolve(`src/${path}`);

try {
  const text = (await readFile(path)).toString();
  const words = text.split(/(?:\r\n|\r|\n)/).length;
  console.log(`${words} words`);
} catch (error) {
  console.error("Error while counting words:", error);
  process.exit(1);
}
