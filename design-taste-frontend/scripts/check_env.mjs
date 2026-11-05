#!/usr/bin/env node
/*
  taste-skill check_env.mjs - Cline port. What the machine needs before the first page.

    node <skill>/scripts/check_env.mjs [--json]

  Checks, in order: Node 22+, a Chrome/Edge/Chromium the check scripts can drive (CHROME_PATH
  first, then the usual places), the kit files this copy runs on, and that library/*.json parse.
  ffmpeg is reported but never required: it only adds WebP and the 780x584 phone crop.

  It installs nothing and changes nothing. A FAIL goes to the user as a fix list, and the run waits
  for their yes (SKILL.md section 0). Exit 1 when something required is missing, 0 when the machine
  can build.
*/
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const here = path.dirname(fileURLToPath(import.meta.url));
const skill = path.resolve(here, '..');
const asJson = process.argv.includes('--json');

const rows = [];
const add = (name, ok, required, detail, fix) => rows.push({ name, ok, required, detail, fix });

// Node 22+ is every script's floor
const major = Number(process.versions.node.split('.')[0]);
add('node', major >= 22, true, `v${process.versions.node}`,
  'install Node 22 or newer from https://nodejs.org, then open the terminal again');

// the same browser list the scripts use; CHROME_PATH wins
const local = process.env.LOCALAPPDATA ? path.join(process.env.LOCALAPPDATA, 'Google/Chrome/Application/chrome.exe') : null;
const browsers = [
  process.env.CHROME_PATH,
  'C:/Program Files/Google/Chrome/Application/chrome.exe',
  'C:/Program Files (x86)/Google/Chrome/Application/chrome.exe',
  local,
  'C:/Program Files/Microsoft/Edge/Application/msedge.exe',
  'C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe',
  '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome',
  '/usr/bin/google-chrome', '/usr/bin/chromium', '/usr/bin/chromium-browser',
].filter(Boolean);
const browser = browsers.find(p => { try { return fs.existsSync(p); } catch { return false; } });
add('browser', Boolean(browser), true, browser || 'none found',
  'install Google Chrome or Microsoft Edge, or set CHROME_PATH to the browser exe (the checkers open it headless)');

// the files a page is built and checked from
const kit = [
  'SKILL.md', 'CLINE.md', 'LICENSE',
  'assets/starter.html', 'assets/system.css', 'assets/system.js',
  'assets/layout/deal.mjs', 'assets/layout/check.mjs', 'assets/layout/heroes.json', 'assets/layout/layout.css',
  'library/palettes.json', 'library/type.json',
  'scripts/start.mjs', 'scripts/consistency.mjs', 'scripts/shoot.mjs', 'scripts/perf.mjs',
  'scripts/photos.mjs', 'scripts/icons.mjs', 'scripts/moments.mjs', 'scripts/effects.mjs',
];
const refs = [
  'backgrounds.md', 'cards.md', 'copy.md', 'diagrams.md', 'effects-creative.md', 'effects-objects.md',
  'effects-usage.md', 'icons.md', 'layout-v4.md', 'moments.md', 'motion.md', 'perf.md', 'photos.md',
  'scenes.md', 'sections-library.md', 'sections.md', 'system.md',
].map(f => `references/${f}`);
const wanted = [...kit, ...refs];
const missing = wanted.filter(f => !fs.existsSync(path.join(skill, f)));
add('kit', missing.length === 0, true,
  missing.length ? `missing ${missing.length}: ${missing.slice(0, 8).join(', ')}${missing.length > 8 ? ', …' : ''}` : `${wanted.length} files in place`,
  `copy the folder again from the repo (${skill}) and re-apply CLINE.md; never delete or edit kit files to pass a check`);

// the dealt data must parse, or start.mjs and deal.mjs stop on the first page
const bad = [];
for (const f of ['library/palettes.json', 'library/type.json']) {
  const p = path.join(skill, f);
  if (!fs.existsSync(p)) continue;   // already reported by the kit row
  try { JSON.parse(fs.readFileSync(p, 'utf8')); } catch (e) { bad.push(`${f} (${e.message.split('\n')[0]})`); }
}
add('library', bad.length === 0, true, bad.length ? bad.join('; ') : 'palettes.json and type.json parse',
  'replace the file with the one from the repo; do not hand-edit the dealt data');

// ffmpeg is a nicety: WebP and the phone crop
const ffmpeg = (() => { try { return spawnSync('ffmpeg', ['-version'], { stdio: 'ignore' }).status === 0; } catch { return false; } })();
add('ffmpeg', ffmpeg, false, ffmpeg ? 'on the path' : 'not on the path',
  'optional: install ffmpeg for WebP files and the 780x584 phone crop; JPEG works without it');

const failed = rows.filter(r => r.required && !r.ok);

if (asJson) {
  console.log(JSON.stringify({ skill, ok: failed.length === 0, rows }, null, 2));
} else {
  console.log(`taste-skill check_env - design-taste-frontend (Cline port)\n${skill}\n`);
  for (const r of rows) {
    const mark = r.ok ? 'ok  ' : r.required ? 'FAIL' : 'warn';
    console.log(`  ${mark}  ${r.name.padEnd(9)} ${r.detail}`);
  }
  if (failed.length) {
    console.log(`\n${failed.length} required item(s) missing. Do not build yet:`);
    console.log('  1. Give this list to the user and ask before installing anything (no silent installs).');
    console.log('  2. Install only what the user agrees to, then run this check again.');
    for (const r of failed) console.log(`  - ${r.name}: ${r.fix}`);
  } else {
    console.log('\nThe machine can build. Next: section 4 of SKILL.md (read the brief, copy assets, deal the hero).');
  }
}

process.exit(failed.length ? 1 : 0);
