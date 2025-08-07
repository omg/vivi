import appRootPath from "app-root-path";
import { mkdir, readFile, writeFile } from "fs/promises";
import { dirname } from "path";

const args = process.argv.slice(2);

if (args.length !== 1) {
  console.error("Usage: tsx convert-to-lua-module <path from src>");
  process.exit(1);
}

let path = args[0];

const hasEnding = path.match(/\..+$/) !== null;
if (!hasEnding) {
  path = path + ".txt";
}

path = appRootPath.resolve(`src/${path}`);

const outputName = path.match(/[/\\]([^/\\]+)\..+$/)[1];
const outputPath = appRootPath.resolve(`dist/${outputName}.luau`);
const outputDir = dirname(outputPath);

try {
  const text = (await readFile(path)).toString();
  const dictionaryString = `[${text
    .split(/(?:\r\n|\r|\n)/)
    .join("][")
    .replace(/"/, '\\"')}]`;
  const result = `return "${dictionaryString}"`;
  await mkdir(outputDir, { recursive: true });
  await writeFile(outputPath, result);
  console.log(`Output result to ${outputPath}`);
} catch (error) {
  console.error("Error writing conversion:", error);
  process.exit(1);
}
