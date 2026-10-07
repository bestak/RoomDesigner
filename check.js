// node check.js: swaps every product in products.js into every matching piece of every built-in layout.
// Each swap has to stay inside the room, and going back to generic has to restore the piece.
const fs = require('fs'), assert = require('assert');
const core = fs.readFileSync(__dirname + '/room.html', 'utf8').match(/<script id="core">([\s\S]*?)<\/script>/)[1];
global.window = {}; require('./products.js');
const { PRESETS, P, applyProduct, catOf, aabb, ROOM, ACCENT, themed, greenery, issues, PAL, GEM, power, along, toWall, DEFAULT_SOCKETS, align, AR_PTS } = new Function(core + '; return { PRESETS, P, applyProduct, catOf, aabb, ROOM, ACCENT, themed, greenery, issues, PAL, GEM, power, along, toWall, DEFAULT_SOCKETS, align, AR_PTS };')();
{ // AR: place the plan corners with a known transform the way three does, then align() has to recover it
  const yaw = 2.5, pos = { x: 1.2, y: -1.4, z: -0.7 }, c = Math.cos(yaw), s = Math.sin(yaw);
  const [h1, h2] = AR_PTS.map(p => ({ x: pos.x + (p.x * c + p.y * s) / 100, y: pos.y, z: pos.z + (p.y * c - p.x * s) / 100 }));
  const a = align(AR_PTS[0], AR_PTS[1], h1, h2);
  assert(Math.abs(Math.sin(a.yaw - yaw)) < 1e-9 && Math.cos(a.yaw - yaw) > 0 && Math.abs(a.measured - ROOM.w) < 1e-9, 'AR alignment angle');
  for (const k of 'xyz') assert(Math.abs(a.pos[k] - pos[k]) < 1e-9, `AR alignment ${k}`);
}
const styleKeys = [PAL, GEM, ACCENT].flatMap(Object.keys);
assert.equal(new Set(styleKeys).size, styleKeys.length, 'two styles share a key, the Style menu would pick the wrong one');

for (const p of Object.values(window.PRODUCTS).flat()) {
  for (const k of ['w', 'd', 'h']) assert(p[k] === undefined || p[k] > 0, `${p.id}: bad ${k}`);
  assert(/^#[0-9A-F]{6}$/i.test(p.color) && (p.price === null || Number.isInteger(p.price)) && p.url && p.img, `${p.id}: bad data`);
}
let n = 0;
for (const list of Object.values(PRESETS)) for (const orig of list) for (const p of window.PRODUCTS[catOf(orig)] || []) {
  const it = applyProduct(structuredClone(orig), p), b = aabb(it);
  assert(b.x0 > -.01 && b.y0 > -.01 && b.x1 < ROOM.w + .01 && b.y1 < ROOM.d + .01, `${p.id} goes through a wall in place of ${orig.id}`);
  applyProduct(it, null);
  for (const k of ['name', 'w', 'd', 'h', 'color', 'color2']) assert.equal(it[k], orig[k], `${p.id} -> generic changed ${k} of ${orig.id}`);
  n++;
}
// a wardrobe standing against the wardrobe wall keeps its back on that wall when it gets deeper
const w = applyProduct(P('wardrobe', 327, 284, 90), window.PRODUCTS.wardrobe.find(p => p.d > 58));
assert(Math.abs(aabb(w).x1 - ROOM.w) < .01, 'deeper wardrobe left the wall');
// plants a style adds never create a new problem or warning
let plants = 0;
for (const [name, list] of Object.entries(PRESETS)) for (const pal of Object.values(ACCENT)) {
  const l = themed(pal, structuredClone(list)), before = issues(l).length, added = greenery(l, pal.plants, pal);
  assert(added <= pal.plants && issues(l).length <= before, `plants for ${pal.label} add problems in ${name}`);
  plants += added;
}
// cables: everything gets connected, and the tree never needs more cable than a separate cable from each light to its nearest socket
let meters = 0;
for (const [name, list] of Object.entries(PRESETS)) {
  const pw = power(list, DEFAULT_SOCKETS), socks = DEFAULT_SOCKETS.map(k => toWall(k.x, k.y)[1]);
  const star = pw.plugs.reduce((t, p) => t + Math.min(...socks.map(s => along(s, p.s).cost)), 0), tree = pw.runs.reduce((t, r) => t + r.cost, 0);
  assert(pw.runs.length === pw.plugs.length && pw.channel <= pw.cable + 1e-6 && tree <= star + 1e-6, `cabling in ${name}`);
  meters += pw.cable / 100;
}
console.log(`ok: ${Object.values(window.PRODUCTS).flat().length} products, ${n} swaps, ${plants} plants placed, ${Math.round(meters)} m of cable planned`);
