// Devpost gallery images (1500x1000, 3:2) from the deployed site's recorded runs, plus the eval slide.
// 1200x800 CSS @1.25. Third-party sites in the hunt table are blurred; one amber outline marks the key element.
import { createRequire } from 'module';
import fs from 'fs'; import path from 'path';
const require = createRequire(process.env.PLAYWRIGHT_DIR || process.env.HOME + '/.claude/skills/gstack/node_modules/');
const { chromium } = require('playwright');
const V = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const SITE = process.env.SITE || 'https://eig-nemotron.onrender.com/';
const CSS = `tr.__blur td:nth-child(n+2){filter:blur(6px)} .__hl{outline:3px solid #f2a900;outline-offset:3px;border-radius:8px;box-shadow:0 0 0 7px rgba(242,169,0,.25)} tr.__row td{background:#fff4d6} tr.__row td:first-child{box-shadow:inset 5px 0 0 #f2a900}`;
const br = await chromium.launch({ args: ['--run-all-compositor-stages-before-draw'] });
const ctx = await br.newContext({ viewport: { width: 1200, height: 800 }, deviceScaleFactor: 1.25, colorScheme: 'light', bypassCSP: true });
async function shot(n, title, prep) {
  const p = await ctx.newPage(); await p.goto(SITE, { waitUntil: 'networkidle', timeout: 120000 });
  await p.addStyleTag({ content: CSS });
  await p.evaluate(() => { Element.prototype.scrollIntoView = function () {}; });
  await p.evaluate(t => [...document.querySelectorAll('.card')].find(c => c.querySelector('h3').textContent === t)
    .querySelector('button.primary').click(), title);
  await p.waitForSelector('#result .verdict'); await p.waitForTimeout(500);
  await p.evaluate(() => document.querySelectorAll('#result tbody tr').forEach(tr => {
    const b = tr.querySelector('.badge'); if (b && b.textContent.trim() === 'unrelated') tr.classList.add('__blur'); }));
  await p.evaluate(prep); await p.waitForTimeout(400);
  await p.screenshot({ path: `${V}/gallery-${n}.png` }); await p.close(); console.log('gallery', n);
}
const top = (sel, off) => `document.scrollingElement.scrollTop = document.querySelector(${JSON.stringify(sel)}).getBoundingClientRect().top + scrollY + ${off}`;
const h3 = t => `[...document.querySelectorAll('#result h3')].find(h => h.textContent.startsWith(${JSON.stringify(t)}))`;
await shot(1, 'Votes moved, totals kept', `document.querySelectorAll('.verdict .box')[2].classList.add('__hl'); ${top('#run', -12)}`);
await shot(2, 'Translations drift', `${top('#result .verdict', -16)}`);
await shot(3, 'Hunt misinformation', `document.querySelectorAll('#result tbody tr')[1].classList.add('__row'); document.querySelectorAll('#result tbody tr')[2].classList.add('__row');
  document.scrollingElement.scrollTop = [...document.querySelectorAll('#result .md *')].find(e => e.textContent.trim() === 'Findings').getBoundingClientRect().top + scrollY - 20`);
// 4: the eval slide from assemble.mjs, laid out at 1600x1067 CSS and captured at 1500x1000.
const src = fs.readFileSync(`${V}/tools/assemble.mjs`, 'utf8');
const slide = src.match(/const SLIDE = `([\s\S]*?)`;/)[1].replace('height:960px', 'height:1067px');
const p = await br.newPage({ viewport: { width: 1600, height: 1067 }, deviceScaleFactor: 1500 / 1600 });
await p.setContent(`<!doctype html><html><body style="margin:0;width:1600px;height:1067px;background:#0f172a;font-family:-apple-system,'SF Pro Text',Helvetica,sans-serif">${slide}</body></html>`);
await p.screenshot({ path: `${V}/gallery-4.png` }); console.log('gallery 4');
await br.close();
