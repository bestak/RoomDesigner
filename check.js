// node check.js: swaps every product in products.js into every matching piece of every built-in layout.
// Each swap has to stay inside the room, and going back to generic has to restore the piece.
const fs = require('fs'), assert = require('assert');
const core = fs.readFileSync(__dirname + '/room.html', 'utf8').match(/<script id="core">([\s\S]*?)<\/script>/)[1];
global.window = {}; require('./products.js');
const { PRESETS, P, applyProduct, catOf, aabb, ROOM } = new Function(core + '; return { PRESETS, P, applyProduct, catOf, aabb, ROOM };')();

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
console.log(`ok: ${Object.values(window.PRODUCTS).flat().length} products, ${n} swaps`);
