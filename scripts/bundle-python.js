import fs from 'fs';
import path from 'path';

const pyDir = path.join(process.cwd(), 'py/bs_lab');
const outDir = path.join(process.cwd(), 'functions');
if (!fs.existsSync(outDir)) fs.mkdirSync(outDir, { recursive: true });

const files = ['core.py', 'iv.py', 'heatmap.py', 'api.py'];
const bundle = {};

files.forEach(f => {
    const content = fs.readFileSync(path.join(pyDir, f), 'utf-8');
    bundle[f] = content;
});

// Add __init__.py
bundle['__init__.py'] = '';

const tsContent = `export const BS_LAB_FILES = ${JSON.stringify(bundle, null, 2)};`;

fs.writeFileSync(path.join(outDir, 'bs_lab_bundle.ts'), tsContent);
console.log('Bundle created at functions/bs_lab_bundle.ts');
