import appRootPath from "app-root-path";
import { mkdir, readFile, writeFile } from "fs/promises";
import { dirname } from "path";
import chardet from "chardet";
import iconv from "iconv-lite";

const args = process.argv.slice(2);

if (args.length !== 1) {
  console.error("Usage: tsx convert-to-lua-module-encode <path from src>");
  process.exit(1);
}

let path = args[0];

const hasEnding = path.match(/\..+$/) !== null;
if (!hasEnding) {
  path = path + ".txt";
}

path = appRootPath.resolve(`src/${path}`);

const outputName = path.match(/[/\\]([^/\\]+)\..+$/)[1];
const outputPath = appRootPath.resolve(`dist/${outputName}.lua`);
const outputDir = dirname(outputPath);

try {
  const buffer = await readFile(path);

  const detectedEncoding = chardet.detect(buffer);
  const encoding = detectedEncoding || "utf-8";

  console.log(`Detected encoding: ${encoding}`);

  const text = iconv.decode(buffer, encoding);

  const result = `return [[\n${text}${text.endsWith("\n") ? "" : "\n"}]]`;

  const outputBuffer = iconv.encode(result, encoding);

  await mkdir(outputDir, { recursive: true });
  await writeFile(outputPath, outputBuffer);
  console.log(`Output result to ${outputPath}`);
} catch (error) {
  console.error("Error writing conversion:", error);
  process.exit(1);
}
