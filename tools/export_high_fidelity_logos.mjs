import { fileURLToPath } from 'node:url';
import { join } from 'node:path';
import sharp from 'sharp';

const imagesDir = fileURLToPath(new URL('../public/images/', import.meta.url));
const logos = [
  { name: 'logo-white', file: 'logo_white.svg' },
  { name: 'logo-black', file: 'logo_black.svg' },
  { name: 'logo-transparent', file: 'logo-transparent.svg' }
];
const sizes = [512, 1024];

async function exportLogos() {
  for (const { name, file } of logos) {
    const source = join(imagesDir, file);
    for (const size of sizes) {
      const target = join(imagesDir, `${name}-${size}.png`);
      await sharp(source)
        .resize(size, size, { fit: 'contain', background: { r: 0, g: 0, b: 0, alpha: 0 } })
        .png({ compressionLevel: 9 })
        .toFile(target);
      console.log(`Created ${target}`);
    }
  }
}

exportLogos().catch((err) => {
  console.error(err);
  process.exit(1);
});
