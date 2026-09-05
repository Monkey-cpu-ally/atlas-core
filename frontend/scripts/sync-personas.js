const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..', '..');
const sourcePath = path.join(root, 'contracts', 'personas.v1.json');
const outputPath = path.join(root, 'frontend', 'src', 'generated', 'personas.v1.json');
const checkOnly = process.argv.includes('--check');

const source = `${JSON.stringify(JSON.parse(fs.readFileSync(sourcePath, 'utf8')), null, 2)}\n`;
const current = fs.existsSync(outputPath) ? fs.readFileSync(outputPath, 'utf8') : '';

if (checkOnly) {
  if (current !== source) {
    console.error('Generated persona registry is stale. Run: yarn sync-personas');
    process.exit(1);
  }
  console.log('Persona registry is synchronized.');
  process.exit(0);
}

fs.mkdirSync(path.dirname(outputPath), { recursive: true });
fs.writeFileSync(outputPath, source);
console.log(`Wrote ${path.relative(root, outputPath)}`);
