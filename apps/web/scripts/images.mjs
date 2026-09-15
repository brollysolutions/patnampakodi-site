import sharp from "sharp";
import { mkdir } from "node:fs/promises";

await mkdir("public/generated", { recursive: true });
// The homepage hero is visible on first load. Prepare its responsive sizes at
// build time so a cold container never resizes it during a customer's request.
for (const width of [384, 768, 1024]) {
  await sharp("public/images/live/signature-erra-karam.webp")
    .resize({ width, withoutEnlargement: true })
    .webp({ quality: 75 })
    .toFile(`public/generated/hero-signature-erra-karam-${width}.webp`);
}
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
