import sharp from "sharp";
import { mkdir } from "node:fs/promises";

await mkdir("public/generated", { recursive: true });
for (const width of [384, 750, 1122]) {
  const source = sharp("public/images/pakodi-illustration.png").resize({
    width,
  });
  await source
    .clone()
    .avif({ quality: 25, effort: 4 })
    .toFile(`public/generated/pakodi-${width}.avif`);
  await source
    .clone()
    .webp({ quality: 45 })
    .toFile(`public/generated/pakodi-${width}.webp`);
}
