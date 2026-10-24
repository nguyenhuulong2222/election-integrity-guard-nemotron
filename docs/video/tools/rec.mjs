// Records the demo shots from the DEPLOYED site (logged out): 1536x864 CSS @1.25 = 1920x1080.
// Scripted steps are rendered frame by frame (deterministic scroll, cursor, highlight); "live" steps click
// "Run live" and capture the real run as it happens, then are time-compressed to a cap with a visible badge.
// Each shot is timed to its narration (docs/video/narr/<id>.wav). Usage: node rec.mjs [s01 ...]
import { createRequire } from 'module';
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';
const require = createRequire(process.env.PLAYWRIGHT_DIR || process.env.HOME + '/.claude/skills/gstack/node_modules/');
const { chromium } = require('playwright');

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const OUT = `${ROOT}/clips`, NARR = `${ROOT}/narr`, FPS = 30;
const SITE = process.env.SITE || 'https://eig-nemotron.onrender.com/';
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());
const card = t => ({ sel: '.card', text: t });
const btn = (t, label) => ({ sel: '.card button', in: card(t), exact: label === 'Run live' && process.env.REPLAY ? 'Replay' : label });
// REPLAY=1 rehearses the shots with recorded runs instead of live ones (no API cost, no rate limit).
const box = i => ({ sel: '.verdict .box', idx: i });
const h3 = t => ({ sel: '#result h3', text: t });

// Steps: {anim, scroll, cursor, hl, fixed?} | {click, settle} | {live, until, cap, scrollTo}
// Times inside an anim are seconds on its nominal `anim` length; non-fixed anims stretch to fit the narration.
const SHOTS = {
  s01: [{ anim: 15, scroll: [{ t: 0, to: 0 }, { t: 10.5, to: 0 }, { t: 13.5, to: { sel: '#pick', off: -24 } }],
    cursor: [{ t: 0, at: [1100, 640] }, { t: 1, at: { sel: '.demo-banner', ax: 0.5 } }, { t: 4.5, at: { sel: '.lede strong', idx: 0, ax: 0.5 } },
      { t: 8, at: { sel: '#routing li', idx: 1, ax: 0.5 } }, { t: 13.5, at: { sel: '#scenarios', ax: 0.5, ay: 0.3 } }],
    hl: [{ from: 0.8, to: 4.2, sel: '.demo-banner' }, { from: 4.6, to: 8, sel: '.lede' }, { from: 8.2, to: 12.5, sel: '#routing' }] }],
  s02: [{ anim: 1.6, fixed: true, scroll: [{ t: 0, to: { sel: '#pick', off: -24 } }],
    cursor: [{ t: 0, at: { sel: '#scenarios', ax: 0.5, ay: 0.3 } }, { t: 1.3, at: btn('Votes moved, totals kept', 'Run live') }],
    hl: [{ from: 0.3, to: 1.6, ...card('Votes moved, totals kept') }] },
  { live: true, click: btn('Votes moved, totals kept', 'Run live'), until: `document.querySelector('#result .verdict')`, cap: 11,
    scrollTo: { sel: '#run', off: -16 } },
  { anim: 8, scroll: [{ t: 0, to: { sel: '#run', off: -16 } }],
    cursor: [{ t: 0, at: { sel: '#steps li', idx: 0, ax: 0.3 } }, { t: 1, at: box(0) }],
    hl: [{ from: 0.2, to: 2.2, sel: '#steps li', idx: 0 }, { from: 1.2, to: 8, ...box(0) }] }],
  s03: [{ anim: 27, scroll: [{ t: 0, to: { sel: '#run', off: -16 } }, { t: 9, to: { sel: '#run', off: -16 } },
      { t: 12, to: { ...h3('Why'), off: -90 } }, { t: 19, to: { ...h3('Why'), off: -90 } }, { t: 21, to: { ...h3('Risk signals'), off: -120 } }],
    cursor: [{ t: 0, at: box(0) }, { t: 1.5, at: box(1) }, { t: 7, at: box(2) }, { t: 12.5, at: { sel: 'ul.evidence li', idx: 0, ax: 0.6 } },
      { t: 21.5, at: { sel: 'ul.evidence', idx: 1, ax: 0.5, ay: 0.2 } }, { t: 26, at: { sel: 'ul.evidence', idx: 1, ax: 0.5, ay: 0.8 } }],
    hl: [{ from: 1, to: 6.5, ...box(1) }, { from: 6.8, to: 11.5, ...box(2) }, { from: 12.3, to: 19.5, sel: 'ul.evidence', idx: 0 },
      { from: 21.3, to: 27, sel: 'ul.evidence', idx: 1 }] }],
  s04: [{ anim: 10, scroll: [{ t: 0, to: { ...h3('Risk signals'), off: -120 } }, { t: 1.2, to: { ...h3('Incident report'), off: -20 } },
      { t: 4.5, to: { ...h3('Incident report'), off: -20 } }, { t: 6, to: { ...h3('Every call'), off: -40 } }],
    cursor: [{ t: 0, at: { sel: 'ul.evidence', idx: 1, ax: 0.5, ay: 0.8 } }, { t: 1.5, at: { ...h3('Incident report'), ax: 0.3 } },
      { t: 6.5, at: { sel: '#result tfoot', ax: 0.9 } }],
    hl: [{ from: 1.4, to: 5, ...h3('Incident report') }, { from: 6.3, to: 10, sel: '#result tfoot' }] }],
  s05: [{ anim: 3, fixed: true, scroll: [{ t: 0, to: 0 }, { t: 0.1, to: { sel: '#pick', off: -24 }, jump: true }],
    cursor: [{ t: 0, at: [900, 500] }, { t: 1.8, at: btn('Documented correction', 'Replay') }],
    hl: [{ from: 0.6, to: 3, ...card('Documented correction') }] },
  { click: btn('Documented correction', 'Replay'), settle: 1500 },
  { anim: 5.5, scroll: [{ t: 0, to: { sel: '#pick', off: -24 } }, { t: 1, to: { sel: '#run', off: -16 } }],
    cursor: [{ t: 0, at: btn('Documented correction', 'Replay') }, { t: 1.5, at: box(2) }],
    hl: [{ from: 1.4, to: 5.5, ...box(2) }] },
  { anim: 2.4, fixed: true, scroll: [{ t: 0, to: { sel: '#run', off: -16 } }, { t: 1.2, to: { sel: '#pick', off: -24 } }],
    cursor: [{ t: 0, at: box(2) }, { t: 2.2, at: btn("Ticket can't be verified", 'Replay') }],
    hl: [{ from: 1.3, to: 2.4, ...card("Ticket can't be verified") }] },
  { click: btn("Ticket can't be verified", 'Replay'), settle: 1500 },
  { anim: 5, scroll: [{ t: 0, to: { sel: '#pick', off: -24 } }, { t: 1, to: { sel: '#run', off: -16 } }],
    cursor: [{ t: 0, at: btn("Ticket can't be verified", 'Replay') }, { t: 1.5, at: box(2) }],
    hl: [{ from: 1.4, to: 5, ...box(2) }] }],
  s06: [{ anim: 2.2, fixed: true, scroll: [{ t: 0, to: 0 }, { t: 0.1, to: { sel: '#pick', off: -24 }, jump: true }],
    cursor: [{ t: 0, at: [900, 500] }, { t: 1.6, at: btn('Translations drift', 'Replay') }],
    hl: [{ from: 0.4, to: 2.2, ...card('Translations drift') }] },
  { click: btn('Translations drift', 'Replay'), settle: 1500 },
  { anim: 22, scroll: [{ t: 0, to: { sel: '#pick', off: -24 } }, { t: 1.2, to: { sel: '#run', off: -16 } }, { t: 6, to: { sel: '#run', off: -16 } },
      { t: 8, to: { sel: '#result .table-wrap', off: -120 } }],
    cursor: [{ t: 0, at: btn('Translations drift', 'Replay') }, { t: 1.6, at: { sel: '#steps li', idx: 0, ax: 0.3 } }, { t: 4, at: { sel: '#steps li', idx: 1, ax: 0.3 } },
      { t: 9, at: { sel: '#result tbody tr', idx: 2, ax: 0.6 } }, { t: 14.5, at: { sel: '#result tbody tr', idx: 0, ax: 0.6 } }, { t: 19, at: { sel: '#result tbody tr', idx: 0, ax: 0.9 } }],
    hl: [{ from: 1.5, to: 4, sel: '#steps li', idx: 0 }, { from: 4, to: 6.5, sel: '#steps li', idx: 1 }, { from: 8.8, to: 13.5, sel: '#result tbody tr', idx: 2 },
      { from: 13.8, to: 18.5, sel: '#result tbody tr', idx: 0 }, { from: 18.8, to: 22, sel: '#result td:last-child', in: { sel: '#result tbody tr', idx: 0 } }] }],
  s07: [{ anim: 1.8, fixed: true, scroll: [{ t: 0, to: 0 }, { t: 0.1, to: { sel: '#pick', off: -24 }, jump: true }],
    cursor: [{ t: 0, at: [900, 500] }, { t: 1.4, at: btn('Hunt misinformation', 'Run live') }],
    hl: [{ from: 0.3, to: 1.8, ...card('Hunt misinformation') }] },
  { live: true, click: btn('Hunt misinformation', 'Run live'), until: `document.querySelector('#result .verdict')`, cap: 9,
    scrollTo: { sel: '#run', off: -16 } },
  { anim: 14, scroll: [{ t: 0, to: { sel: '#run', off: -16 } }, { t: 3, to: { sel: '#run', off: -16 } }, { t: 4.5, to: { ...h3('Report'), off: -40 } },
      { t: 8.5, to: { ...h3('Report'), off: -40 } }, { t: 10, to: { ...h3('Every result'), off: -30 } }],
    cursor: [{ t: 0, at: { sel: '#steps li', idx: 0, ax: 0.3 } }, { t: 1.5, at: box(0) }, { t: 3.2, at: box(1) }, { t: 5, at: { ...h3('Report'), ax: 0.3 } },
      { t: 10.5, at: { sel: '#result tbody tr', idx: 1, ax: 0.35 } }, { t: 13, at: { sel: '#result tbody tr', idx: 2, ax: 0.35 } }],
    hl: [{ from: 0.1, to: 1.6, sel: '#steps li', idx: 0 }, { from: 1.4, to: 3, ...box(0) }, { from: 3, to: 4.4, ...box(1) },
      { from: 10.3, to: 14, sel: '#result tbody tr', idx: 1 }, { from: 10.3, to: 14, sel: '#result tbody tr', idx: 2 }] }],
};
const LEAD = 1.4; // seconds of picture beyond the narration (assembly adds 0.4 s before the voice)

const INIT = `(()=>{
window.__find=(q)=>{ if(Array.isArray(q)) return null;
  let root=document; if(q.in){ root=__find(q.in); if(!root) return null; }
  let els=[...root.querySelectorAll(q.sel||'*')];
  if(q.text) els=els.filter(e=>(e.innerText||'').includes(q.text)).sort((a,b)=>a.innerText.length-b.innerText.length);
  if(q.exact) els=els.filter(e=>(e.innerText||'').trim()===q.exact);
  return els[q.text?0:(q.idx||0)]||null;};
window.__pt=(q)=>{ if(Array.isArray(q)) return q; const e=__find(q); if(!e) return [768,432]; const b=e.getBoundingClientRect();
  return [b.x+b.width*Math.min(q.ax??0.5,1), b.y+b.height*(q.ay??0.5)];};
Element.prototype.scrollIntoView=function(){};   // the recorder owns scrolling
// Blur third-party sites in the hunt table: only the demo's own pages stay readable.
new MutationObserver(()=>document.querySelectorAll('#result tbody tr').forEach(tr=>{
  const b=tr.querySelector('.badge'); if(b&&b.textContent.trim()==='unrelated') tr.classList.add('__blur');})).observe(document.body,{subtree:true,childList:true});
})()`;
const CSS = `#__cur{position:fixed;z-index:2147483647;pointer-events:none;width:44px;height:44px;margin:-6px 0 0 -6px}
 #__cur .halo{position:absolute;left:-14px;top:-14px;width:40px;height:40px;border-radius:50%;background:rgba(255,196,0,.35)}
 .__hl{position:fixed;z-index:2147483646;pointer-events:none;border:3px solid #f2a900;border-radius:8px;box-shadow:0 0 0 4px rgba(242,169,0,.25),0 0 18px rgba(242,169,0,.45)}
 tr.__blur td:nth-child(n+2){filter:blur(6px)} *{caret-color:transparent!important;scroll-behavior:auto!important}`;
const CURSOR = `<div class="halo"></div><svg width="28" height="34" viewBox="0 0 28 34" style="position:absolute;left:0;top:0"><path d="M2 2 L2 27 L8.5 21 L13 31 L17.5 29 L13 19.5 L22 19.5 Z" fill="#111" stroke="#fff" stroke-width="2" stroke-linejoin="round"/></svg>`;

const ease = x => x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
function seg(keys, t) {
  let i = 0; while (i < keys.length - 1 && keys[i + 1].t <= t) i++;
  const a = keys[i], b = keys[i + 1]; if (!b || b.jump) return [a, a, 1];
  return [a, b, ease((t - a.t) / (b.t - a.t))];
}
// Draw one frame: scroll, cursor and highlight state. Returns a key so identical frames are hard-linked.
const draw = (p, st) => p.evaluate(async ({ sa, sb, sp, ca, cb, cp, hl, hls }) => {
  const el = document.scrollingElement;
  const top = q => { if (typeof q === 'number') return q; const e = __find(q); return e ? e.getBoundingClientRect().top + el.scrollTop + (q.off || 0) : el.scrollTop; };
  const y = top(sa.to) + (top(sb.to) - top(sa.to)) * sp; el.scrollTop = Math.round(y);
  const A = __pt(ca.at), B = __pt(cb.at); const x = A[0] + (B[0] - A[0]) * cp, yy = A[1] + (B[1] - A[1]) * cp;
  const c = document.getElementById('__cur'); c.style.left = Math.round(x) + 'px'; c.style.top = Math.round(yy) + 'px';
  document.querySelectorAll('.__hl').forEach(n => n.remove());
  hl.forEach((h, i) => { if (hls[i] <= 0) return; const e = __find(h); if (!e) return; const b = e.getBoundingClientRect();
    const d = document.createElement('div'); d.className = '__hl';
    Object.assign(d.style, { left: (b.x - 6) + 'px', top: (b.y - 5) + 'px', width: (b.width + 12) + 'px', height: (b.height + 10) + 'px', opacity: hls[i] });
    document.body.appendChild(d); });
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));   // no torn frames mid-scroll
  return [el.scrollTop, Math.round(x), Math.round(yy), hls.map(v => v.toFixed(2)).join()].join('|');
}, st);

const only = process.argv.slice(2);
fs.mkdirSync(OUT, { recursive: true });
const br = await chromium.launch({ args: ['--run-all-compositor-stages-before-draw', '--disable-checker-imaging'] });   // no stale raster tiles in screenshots
const ctx = await br.newContext({ viewport: { width: 1536, height: 864 }, deviceScaleFactor: 1.25, colorScheme: 'light', bypassCSP: true });
let page = null, prevShotLast = null;
for (const [name, steps] of Object.entries(SHOTS)) {
  if (only.length && !only.includes(name)) continue;
  // s02-s04 continue on the same page (the live tamper result); every other shot starts fresh.
  const cont = ['s03', 's04'].includes(name) && page && prevShotLast;
  if (!cont) { if (page) await page.close(); page = await ctx.newPage();
    await page.goto(SITE, { waitUntil: 'networkidle', timeout: 120000 });
    await page.waitForSelector('.card button'); await page.evaluate(INIT); await page.addStyleTag({ content: CSS });
    await page.evaluate(h => { const c = document.createElement('div'); c.id = '__cur'; c.innerHTML = h; document.body.appendChild(c); }, CURSOR);
    await page.waitForTimeout(800); }
  const p = page;
  const target = dur(`${NARR}/${name}.wav`) + LEAD;
  const dir = `${OUT}/${name}_frames`; fs.rmSync(dir, { recursive: true, force: true }); fs.mkdirSync(dir);
  const frames = []; const badges = []; let n = 0, prevKey = null, prevFile = null, cursorAt = null;
  const shoot = async key => { const file = `${dir}/${String(n++).padStart(5, '0')}.jpg`;
    if (key && key === prevKey) fs.linkSync(prevFile, file); else { await p.screenshot({ path: file, type: 'jpeg', quality: 93 }); prevKey = key; prevFile = file; }
    return file; };
  for (const [si, S] of steps.entries()) {
    if (S.click && !S.live) { await p.evaluate(q => __find(q).click(), S.click); await p.waitForTimeout(S.settle); prevKey = null; continue; }
    if (S.live) {
      await p.evaluate(q => __find(q).click(), S.click);
      const y0 = await p.evaluate(() => document.scrollingElement.scrollTop);
      const raw = []; const t0 = Date.now(); let doneAt = null;
      while (true) {
        const t = (Date.now() - t0) / 1000;
        await p.evaluate(({ q, y0, k }) => { const el = document.scrollingElement, e = __find(q);
          const y1 = e ? e.getBoundingClientRect().top + el.scrollTop + (q.off || 0) : y0;
          el.scrollTop = Math.round(y0 + (y1 - y0) * k); document.querySelectorAll('.__hl').forEach(x => x.remove());
          return new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r))); },
          { q: S.scrollTo, y0, k: ease(Math.min(1, t / 1.0)) });
        raw.push([t, await shoot(null)]);
        if (!doneAt && await p.evaluate(S.until)) doneAt = t;
        if (doneAt && t - doneAt > 0.6) break;
        if (t > 150) throw new Error(`${name}: live run did not finish`);
        const err = await p.evaluate(() => !document.querySelector('#run-error').hidden && document.querySelector('#run-error').textContent);
        if (err) throw new Error(`${name}: live run failed: ${err}`);
      }
      const real = raw.at(-1)[0], len = Math.min(real, S.cap), k = real / len, start = frames.length / FPS;
      for (let f = 0; f < Math.round(len * FPS); f++) { const ts = f / FPS * k; let j = 0; while (j < raw.length - 1 && raw[j + 1][0] <= ts) j++; frames.push(raw[j][1]); }
      if (k > 1.05) badges.push([start + 1.0, start + len, k]);
      console.log(`${name} live: ${real.toFixed(1)} s real -> ${len.toFixed(1)} s (x${k.toFixed(2)})`);
      prevKey = null; continue;
    }
    // Scripted anim: stretch non-fixed anims to fill the rest of the narration.
    let len = S.anim;
    if (!S.fixed) { const later = steps.slice(si + 1);
      if (!later.some(x => x.live)) { const fixedLater = later.filter(x => x.anim && x.fixed).reduce((a, x) => a + x.anim, 0);
        const flex = [S, ...later].filter(x => x.anim && !x.fixed).reduce((a, x) => a + x.anim, 0);
        len = Math.max(1, (target - frames.length / FPS - fixedLater) * S.anim / flex); } }
    const k = len / S.anim, N = Math.round(len * FPS);
    for (let f = 0; f < N; f++) {
      const t = f / FPS / k;
      const [sa, sb, sp] = seg(S.scroll, t), [ca, cb, cp] = seg(S.cursor, t);
      const hls = S.hl.map(h => Math.max(0, Math.min(1, (t - h.from) / 0.3, (h.to - t) / 0.3)));
      const key = await draw(p, { sa, sb, sp, ca, cb, cp, hl: S.hl, hls });
      frames.push(await shoot(key));
    }
  }
  prevShotLast = true;
  // frames -> mp4 at 30 fps (concat list of 1/30 s entries), then the "sped up" badges.
  const list = `${dir}/list.txt`;
  fs.writeFileSync(list, 'ffconcat version 1.0\n' + [...frames, frames.at(-1)].map(f => `file '${f}'\nduration ${1 / FPS}`).join('\n') + '\n');
  const args = ['-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', list];
  let vf = 'fps=30,scale=1920:1080:flags=lanczos';
  for (const [bi, [a, b, k]] of badges.entries()) {
    const png = `${dir}/badge${bi}.png`, bp = await ctx.newPage();
    await bp.setViewportSize({ width: 360, height: 76 });
    await bp.setContent(`<body style="margin:0;background:transparent"><div style="margin:8px;display:inline-block;padding:10px 20px;border-radius:12px;background:rgba(15,23,42,.85);color:#fff;font:600 30px -apple-system,Helvetica,sans-serif">⏩ Sped up ${k.toFixed(1)}×</div></body>`);
    await bp.screenshot({ path: png, omitBackground: true }); await bp.close();
    args.push('-i', png); vf += `[v${bi}];[v${bi}][${bi + 1}:v]overlay=W-w-40:150:enable='between(t,${a.toFixed(2)},${b.toFixed(2)})'`;
  }
  args.push('-filter_complex', `[0:v]${vf},format=yuv420p[out]`, '-map', '[out]',
    '-c:v', 'libx264', '-crf', '16', '-preset', 'medium', '-r', String(FPS), `${OUT}/${name}.mp4`);
  execFileSync('ffmpeg', args);
  fs.rmSync(dir, { recursive: true, force: true });
  console.log(name, 'done', (frames.length / FPS).toFixed(1), 's (target', target.toFixed(1) + ')');
}
await br.close();
