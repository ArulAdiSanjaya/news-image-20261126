// main.ts — entry program for news-image-20261126.
//
// Copies the repository's entry.png to the output directory, after
// validating that it is a whole PNG within the competition limits
// (at most 1024x1024 pixels, at most 1 MiB). The copy is byte for byte
// identical on every run, so the two grader runs write the same bytes.
//
// Runs on Node 22 with the standard library only; no network access.

import { createHash } from "node:crypto";
import { copyFileSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1048576;
const MAX_DIM = 1024;

const PNG_SIGNATURE = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a,
]);

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

function sha256Hex(path: string): string {
  const data = readFileSync(path);
  return createHash("sha256").update(data).digest("hex");
}

function main(): void {
  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");
  const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
  const target = join(outDir, "entry.png");

  let bytes: Buffer;
  try {
    bytes = readFileSync(source);
  } catch {
    fail(`cannot read ${source}`);
  }

  if (bytes.length > MAX_BYTES) {
    fail(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  if (!bytes.subarray(0, 8).equals(PNG_SIGNATURE)) {
    fail("entry.png does not start with the PNG signature");
  }

  // Parse the IHDR chunk: length (4) + "IHDR" (4) + width (4) + height (4).
  if (bytes.length < 33 || bytes.toString("latin1", 12, 16) !== "IHDR") {
    fail("entry.png has no IHDR chunk where expected");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  if (width === 0 || height === 0 || width > MAX_DIM || height > MAX_DIM) {
    fail(`entry.png is ${width}x${height}, over the ${MAX_DIM}x${MAX_DIM} limit`);
  }

  // The file must be a whole PNG: it ends with the IEND chunk
  // (4 zero length bytes, the letters IEND, then its CRC).
  const tail = bytes.subarray(bytes.length - 12);
  if (tail.readUInt32BE(0) !== 0 || tail.toString("latin1", 4, 8) !== "IEND") {
    fail("entry.png does not end with the IEND chunk");
  }

  mkdirSync(outDir, { recursive: true });
  copyFileSync(source, target);

  const outSize = statSync(target).size;
  if (outSize !== bytes.length) {
    fail(`wrote ${outSize} bytes, expected ${bytes.length}`);
  }
  if (sha256Hex(target) !== sha256Hex(source)) {
    fail("output sha256 does not match entry.png");
  }

  console.log(
    `wrote ${target} (${width}x${height}, ${outSize} bytes, ` +
      `sha256 ${sha256Hex(target)})`,
  );
}

main();
