import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import sharp from 'sharp';

const imagesDir = fileURLToPath(new URL('../public/images/', import.meta.url));
const variants = [
  { name: 'light', file: 'favicon-light.svg' },
  { name: 'dark', file: 'favicon-dark.svg' }
];
const sizes = [16, 32, 48, 64, 128, 256, 512];

async function generate() {
  for (const { name, file } of variants) {
    const source = join(imagesDir, file);
    for (const size of sizes) {
      const target = join(imagesDir, `mind-favicon-${name}-${size}.png`);
      await sharp(source)
        .resize(size, size)
        .png({ compressionLevel: 9 })
        .toFile(target);
      console.log(`Created ${target}`);
    }
  }
}

generate().catch((err) => {
  console.error(err);
  process.exit(1);
});
