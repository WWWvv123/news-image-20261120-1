import { copyFileSync, existsSync, readFileSync, statSync, mkdirSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, "entry.png");
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? join(here, "out");
const target = join(outDir, "entry.png");

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

if (!existsSync(target)) {
  throw new Error("entry.png was not copied to the output directory");
}
const bytes = readFileSync(target);
if (bytes.length > 1024 * 1024) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
if (
  bytes[0] !== 0x89 || bytes[1] !== 0x50 || bytes[2] !== 0x4e ||
  bytes[3] !== 0x47 || bytes[4] !== 0x0d || bytes[5] !== 0x0a ||
  bytes[6] !== 0x1a || bytes[7] !== 0x0a
) {
  throw new Error("entry.png is not a PNG file");
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}
const sha256 = createHash("sha256").update(bytes).digest("hex");
console.log(`entry.png: ${statSync(target).size} bytes, ${width}x${height}`);
console.log(`sha256: ${sha256}`);
console.log(`copied to ${target}`);
