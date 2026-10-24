// Assembles the demo: recorded clips + narration + caption overlays (+ an eval slide and end card for the
// last shot) -> docs/video/nemotron-integrity-agent-demo.mp4 (1920x1080, 30 fps, no music).
import { createRequire } from 'module';
import fs from 'fs'; import path from 'path'; import { execFileSync } from 'child_process';
const require = createRequire(process.env.PLAYWRIGHT_DIR || process.env.HOME + '/.claude/skills/gstack/node_modules/');
const { chromium } = require('playwright');

const V = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..');
const W = `${V}/build`; fs.mkdirSync(W, { recursive: true });
const LEAD = 0.4, FADE = 0.2, CAPTIONS = process.env.CAPTIONS !== '0';
const ff = (...a) => execFileSync('ffmpeg', ['-y', '-loglevel', 'error', ...a]);
const dur = f => parseFloat(execFileSync('ffprobe', ['-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).toString());

const FONT = `-apple-system,'SF Pro Text',Helvetica,sans-serif`;
const SLIDE = `<div style="box-sizing:border-box;height:960px;display:flex;flex-direction:column;justify-content:center;padding:0 120px;color:#e2e8f0">
 <div style="font-size:26px;letter-spacing:.08em;text-transform:uppercase;color:#94a3b8">Measured honestly · small fixture sets · 2 runs per case</div>
 <div style="font-size:54px;font-weight:700;margin:14px 0 34px;color:#fff">Detection is deterministic. Nemotron routes.</div>
 <div style="display:grid;grid-template-columns:1fr 1fr;gap:44px">
  <div style="background:#1e293b;border-radius:18px;padding:30px 36px">
   <div style="font-size:24px;color:#94a3b8">Translation drift · FAST extraction · 7 scenarios × 2 runs</div>
   <table style="width:100%;margin-top:18px;font-size:30px;border-collapse:collapse">
    <tr style="color:#94a3b8;font-size:22px"><td></td><td>Exactly right</td><td>Precision</td></tr>
    <tr><td style="padding:10px 0;font-weight:700;color:#86efac">Lightning</td><td style="font-weight:700;color:#86efac">14 / 14</td><td>1.00</td></tr>
    <tr><td style="padding:10px 0">Nano 30B</td><td>3 / 14</td><td>0.54</td></tr></table>
  </div>
  <div style="background:#1e293b;border-radius:18px;padding:30px 36px">
   <div style="font-size:24px;color:#94a3b8">Tamper triage · Super · held-out set H08–H14, committed before running</div>
   <table style="width:100%;margin-top:18px;font-size:28px;border-collapse:collapse">
    <tr style="color:#94a3b8;font-size:22px"><td></td><td>Gate v1</td><td>Gate v2</td></tr>
    <tr><td style="padding:8px 0">Correct decisions</td><td>8 / 14</td><td>9 / 14</td></tr>
    <tr><td style="padding:8px 0">False rollbacks</td><td>1 / 8</td><td>1 / 8</td></tr>
    <tr><td style="padding:8px 0;color:#fca5a5">Disguised tampering<br>sent to sign-off</td><td style="color:#fca5a5">5 / 6</td><td style="color:#fca5a5">3 / 6</td></tr></table>
  </div>
 </div>
 <div style="margin-top:34px;font-size:30px;color:#cbd5e1">Every miss was still <b style="color:#fff">detected by the Results Seal</b> and routed to an official. Nothing is silently accepted.</div>
</div>`;
const END = `<div style="display:flex;flex-direction:column;height:100%;align-items:center;justify-content:center;color:#e2e8f0;text-align:center">
 <div style="font-size:84px;font-weight:700;color:#fff">Nemotron Integrity Agent</div>
 <div style="font-size:36px;margin-top:18px;color:#cbd5e1">NVIDIA Nemotron on Nebius Token Factory · Tavily</div>
 <div style="font-size:32px;margin-top:56px;font-family:ui-monospace,Menlo,monospace;line-height:1.7">eig-nemotron.onrender.com<br>github.com/nguyenhuulong2222/election-integrity-guard-nemotron</div>
 <div style="font-size:24px;margin-top:56px;color:#94a3b8">Open source (MIT) · Fictional demo data · AI-generated narration</div></div>`;

// [narration id, video source]
const SEG = [['s01', { clip: 's01' }], ['s02', { clip: 's02' }], ['s03', { clip: 's03' }], ['s04', { clip: 's04' }],
  ['s05', { clip: 's05' }], ['s06', { clip: 's06' }], ['s07', { clip: 's07' }], ['s08', { cards: [[SLIDE, 0.74], [END, 0.26]] }]];

const br = await chromium.launch(); const pg = await br.newPage({ viewport: { width: 1920, height: 1080 } });
async function png(html, file, transparent) {
  await pg.setContent(`<!doctype html><html><body style="margin:0;width:1920px;height:1080px;${transparent ? 'background:transparent' : 'background:#0f172a'};font-family:${FONT}">${html}</body></html>`);
  await pg.screenshot({ path: file, omitBackground: !!transparent });
}
function chunks(t) { // caption lines of about 68 characters, split at sentence or clause boundaries
  const parts = t.match(/[^.;:!?]+[.;:!?]+["']?|[^.;:!?]+$/g).map(s => s.trim()); const out = [];
  for (const p of parts) { if (p.length <= 68) { out.push(p); continue; }
    const w = p.split(' '); let cur = ''; const n = Math.ceil(p.length / 62), tgt = p.length / n;
    for (const x of w) { if (cur && (cur + ' ' + x).length > tgt + 6) { out.push(cur); cur = x; } else cur = cur ? cur + ' ' + x : x; }
    if (cur) out.push(cur); }
  return out;
}
const list = [];
for (const [i, [id, src]] of SEG.entries()) {
  const narr = `${V}/narr/${id}.wav`, nd = dur(narr), text = fs.readFileSync(`${V}/narr/${id}.txt`, 'utf8');
  let vin;
  if (src.clip) vin = `${V}/clips/${src.clip}.mp4`;
  else { // slides: each card gets its share of the narration length
    const total = nd + LEAD + 1.4, parts = [];
    for (const [k, [html, share]] of src.cards.entries()) {
      const p = `${W}/${id}_card${k}.png`, v = `${W}/${id}_card${k}.mp4`; await png(html, p);
      ff('-loop', '1', '-i', p, '-t', (total * share).toFixed(3), '-r', '30', '-vf', 'format=yuv420p', '-c:v', 'libx264', '-crf', '18', v); parts.push(v); }
    vin = `${W}/${id}_v.mp4`; fs.writeFileSync(`${W}/${id}.txt`, parts.map(c => `file '${c}'`).join('\n'));
    ff('-f', 'concat', '-safe', '0', '-i', `${W}/${id}.txt`, '-c', 'copy', vin);
  }
  const d = Math.max(dur(vin), nd + LEAD + 0.3);
  const caps = []; if (CAPTIONS) { const cs = chunks(text), tot = cs.reduce((a, c) => a + c.length, 0); let t = LEAD;
    for (const [k, c] of cs.entries()) { const cd = nd * c.length / tot, f = `${W}/${id}_cap${k}.png`;
      await png(`<div style="position:absolute;left:0;right:0;bottom:44px;text-align:center"><span style="display:inline-block;max-width:1500px;padding:10px 22px;border-radius:10px;background:rgba(15,23,42,.78);color:#fff;font-size:34px;line-height:1.3;font-weight:500">${c.replace(/&/g, '&amp;').replace(/</g, '&lt;')}</span></div>`, f, true);
      caps.push([f, t, t + cd]); t += cd; } }
  const args = ['-i', vin, '-i', narr]; caps.forEach(c => args.push('-i', c[0]));
  let fc = `[0:v]tpad=stop_mode=clone:stop_duration=${d},trim=0:${d},setpts=PTS-STARTPTS[v0]`;
  caps.forEach((c, k) => { fc += `;[v${k}][${k + 2}:v]overlay=0:0:enable='between(t,${c[1].toFixed(3)},${c[2].toFixed(3)})'[v${k + 1}]`; });
  const fin = i === 0 ? 'fade=in:st=0:d=0.5,' : `fade=in:st=0:d=${FADE},`;
  const fout = i === SEG.length - 1 ? `fade=out:st=${(d - 0.8).toFixed(3)}:d=0.8` : `fade=out:st=${(d - FADE).toFixed(3)}:d=${FADE}`;
  fc += `;[v${caps.length}]${fin}${fout},format=yuv420p[vo];[1:a]aresample=48000,adelay=${LEAD * 1000}:all=1,apad,atrim=0:${d}[ao]`;
  const out = `${W}/${String(i).padStart(2, '0')}_${id}.mp4`;
  ff(...args, '-filter_complex', fc, '-map', '[vo]', '-map', '[ao]', '-r', '30', '-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-c:a', 'aac', '-b:a', '192k', '-ac', '2', out);
  list.push(out); console.log(id, d.toFixed(2), 's');
}
await br.close();
fs.writeFileSync(`${W}/list.txt`, list.map(f => `file '${f}'`).join('\n'));
const OUT = `${V}/nemotron-integrity-agent-demo.mp4`;
ff('-f', 'concat', '-safe', '0', '-i', `${W}/list.txt`, '-c', 'copy', '-movflags', '+faststart', OUT);
console.log(OUT, dur(OUT).toFixed(2), 's');
