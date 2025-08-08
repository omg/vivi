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
const outputTypePath = appRootPath.resolve(`dist/${outputName}.d.ts`);
const outputDir = dirname(outputPath);

function dashToPascalCase(input: string): string {
  return input
    .split("-")
    .map((word) => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase())
    .join("");
}

const outputPascalName = dashToPascalCase(outputName);

try {
  const text = (await readFile(path)).toString();
  const dictionaryString = `[${text
    .split(/(?:\r\n|\r|\n)/)
    .join("][")
    .replace(/"/, '\\"')}]`;
  const result = `return "${dictionaryString}"\n`;
  const typeResult = `declare const ${outputPascalName}: string;\nexport = ${outputPascalName};\n`;
  await mkdir(outputDir, { recursive: true });
  await writeFile(outputPath, result);
  await writeFile(outputTypePath, typeResult);
  console.log(`Output result to ${outputPath}`);
} catch (error) {
  console.error("Error writing conversion:", error);
  process.exit(1);
}
