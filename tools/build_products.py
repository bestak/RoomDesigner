# python3 tools/build_products.py: builds products.js from the scraped JSON (name, price, url, photo) plus this hand-checked table
# (size in the planner's terms, colours read off the photos, shape hints for the 3D view).
import json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))

src = {}
for f in ['ikea.jsonl', 'jysk.jsonl', 'bazos_pick.jsonl', 'extra.jsonl']:
    for l in open(os.path.join(HERE, 'data', f)):
        r = json.loads(l); src[r['n']] = r

# n: (w, d, h, color, color2, look, short name, note)   w = along the front, d = front to back
P = {
  # beds: h = headboard height, look.top = mattress top
  0: (94, 205, 65, '#DCC096', None, dict(top=44, legs=1, head=65, foot=30), 'NEIDEN, borovice', ''),
  1: (105, 209, 100, '#EDEDEA', None, dict(top=50, head=100, foot=38), 'MALM vysoký, bílá', ''),
  2: (96, 207, 27, '#EEEEEB', None, dict(top=40, legs=1, head=27, foot=27, thin=1), 'VEVELSTAD, bílá', 'Thin metal frame.'),
  3: (99, 209, 101, '#3F2E26', None, dict(top=50, head=101, foot=39), 'STORKLINTA, tmavý dub', 'Price includes the LURÖY slats.'),
  100: (100, 207, 101, '#A87D4F', None, dict(top=48, head=101, foot=45), 'VEDDE, divoký dub', ''),
  101: (95, 205, 91, '#C9A77F', None, dict(top=50, head=91, foot=50, drawers=2), 'LIMFJORDEN, 2 zásuvky', ''),
  102: (104, 216, 101, '#C9C3BC', None, dict(top=48, legs=1, legc='#C9A06D', head=101, foot=35, soft=1), 'KONGSBERG, béžový potah', ''),
  # nightstands and dressers: drawers from the top, open = open shelf height at the bottom, legs = leg height
  4: (39, 41, 53, '#EEEEEA', None, dict(drawers=1, open=22), 'BRIMNES, bílá', ''),
  5: (39, 32, 55, '#D9BC93', None, dict(drawers=1, open=16, legs=18), 'KRONÖREN, borovice', ''),
  6: (40, 40, 59, '#C4A07A', None, dict(drawers=1, open=24, legs=11), 'TONSTAD, dub', ''),
  7: (54, 38, 58, '#6E5038', None, dict(drawers=1, open=10, legs=32, legc='#1F2124'), 'RÅDMANSÖ, ořech', ''),
  103: (45, 33, 55, '#B8956B', None, dict(drawers=1, legs=34), 'HOKKSUND, dub', ''),
  104: (41, 48, 56, '#C2A488', None, dict(drawers=2), 'LIMFJORDEN, světlý dub', ''),
  200: (40, 35, 55, '#EEEDEA', None, dict(drawers=1, open=20, legs=10, top='#4A3326'), 'Noční stolek, masiv', ''),
  8: (80, 42, 100, '#EEEEEA', None, dict(drawers=4, legs=3), 'LASTARE, bílá', ''),
  9: (78, 46, 95, '#EEEEEA', None, dict(drawers=3), 'BRIMNES, bílá', ''),
  10: (90, 48, 81, '#7A5A40', None, dict(drawers=3, legs=13, legc='#1F2124'), 'RÅDMANSÖ, ořech', ''),
  11: (82, 47, 90, '#B8956A', None, dict(drawers=4, legs=5), 'TONSTAD, dub', ''),
  12: (70, 40, 112, '#EEEEEA', None, dict(drawers=5), 'KULLEN, bílá', ''),
  105: (81, 48, 101, '#C4A88C', None, dict(drawers=4), 'LIMFJORDEN, světlý dub', ''),
  106: (81, 45, 102, '#CFA878', None, dict(drawers=4, legs=4), 'TRANUM, zlatý dub', ''),
  201: (80, 48, 77.5, '#B98E62', None, dict(drawers=3), 'MALM, dub', ''),
  202: (75, 42, 80, '#C9B69C', None, dict(drawers=3), 'Komoda, dekor dub', ''),
  # wardrobes
  13: (117, 50, 190, '#EEEEEA', None, dict(doors=3, mirror=1), 'BRIMNES, 3 dveře', ''),
  14: (117, 55, 176, '#EEEEEA', None, dict(doors=3), 'KLEPPSTAD, 3 dveře', ''),
  15: (128, 64, 201, '#EEEEEA', None, dict(doors=3, drawers=2, legs=8), 'GULLABERG', ''),
  16: (120, 57, 241, '#EEEEEA', None, dict(doors=2, drawers=0), 'PLATSA, 4 dveře + 3 zás.', ''),
  107: (120, 58, 200, '#CBB79E', None, dict(doors=2, drawers=3), 'LIMFJORDEN, světlý dub', ''),
  108: (109, 61, 220, '#C8996B', None, dict(doors=2), 'LINTRUP, dub', ''),
  203: (120, 55, 195, '#EEEEEA', None, dict(doors=3, mirror=1), 'Karl (ASKO), bílá', ''),
  300: (97, 50, 176, '#CDB5A0', None, dict(doors=2, drawers=3, stack=1), 'FANDRUP, světlý dub', 'Three drawers under the right door.'),
  204: (120, 58, 161, '#5A3A26', None, dict(doors=2, legs=10), 'Retro skříň, Rousínov', ''),
  # KALLAX-style shelving
  17: (147, 39, 147, '#EEEEEA', None, None, 'KALLAX 4×4, bílá', ''),
  18: (147, 39, 147, '#D2C2AC', None, None, 'KALLAX 4×4, bíle mořený dub', ''),
  19: (182, 39, 182, '#EEEEEA', None, None, 'KALLAX 5×5, bílá', ''),
  20: (76.5, 39, 147, '#7A5E4E', None, None, 'KALLAX 2×4, ořech', ''),
  21: (147, 39, 77, '#6E3F43', None, None, 'KALLAX 4×2, hnědočervená', ''),
  121: (100, 35, 140, '#9B8467', None, None, 'GADEHUSE dělicí stěna', ''),
  205: (147, 39, 147, '#EEEEEA', None, None, 'KALLAX 4×4, bílá', ''),
  # armchairs: kind = wood (open oak frame) | poang | wing | shell
  22: (68, 82, 100, '#D8D0C4', '#E1C79E', dict(kind='poang'), 'POÄNG, bříza/béžová', ''),
  23: (65, 74, 75, '#CFC5B9', '#C9A36F', dict(kind='wood'), 'EKENÄSET, dub/béžová', ''),
  24: (82, 96, 101, '#8C7D66', '#4A3526', dict(kind='wing'), 'STRANDMON ušák, béžová/hnědá', 'Checked fabric.'),
  25: (71, 66, 73, '#7E7E7E', '#1F2124', dict(kind='shell'), 'HERRÅKRA, šedá', ''),
  109: (66, 68, 84, '#D3CBC6', '#C9A06D', dict(kind='shell'), 'UDSBJERG, béžová/dub', ''),
  110: (72, 80, 98, '#5E6448', '#C9A06D', dict(kind='wing'), 'HUNDESTED, zelený manšestr', ''),
  206: (68, 82, 100, '#B8A58E', '#D5B58A', dict(kind='poang'), 'POÄNG', 'Size taken from IKEA.'),
  207: (82, 96, 101, '#C4A97E', '#5A3F2C', dict(kind='wing'), 'STRANDMON, Kelinge béžová', 'Size taken from IKEA.'),
  # coffee and side tables
  26: (70, 70, 42, '#D6BF9A', None, dict(legs='four', shelf=1), 'BORGEBY, bříza', ''),
  27: (55, 55, 45, '#EFEFEA', None, dict(shape='rect', legs='thick'), 'LACK, bílá', ''),
  28: (45, 45, 53, '#2A2A2A', None, dict(legs='thin'), 'GLADOM, černá', ''),
  29: (50, 50, 50, '#B08D6E', None, dict(shape='rect', legs='solid'), 'HOL, akácie', ''),
  111: (70, 70, 45, '#B99A76', None, dict(legs='pedestal'), 'KALVEHAVE, dub', ''),
  112: (55, 55, 45, '#F2F1EC', '#C0916A', dict(shape='rect', legs='splay'), 'TAPS, bílá/bambus', ''),
  # office chairs
  30: (62, 60, 129, '#3A3A3A', None, None, 'MARKUS, tmavě šedá', ''),
  31: (71, 71, 114, '#D8CCC4', None, None, 'FLINTAN, béžová', ''),
  32: (70, 70, 123, '#2E2E2E', None, None, 'MILLBERGET, černá', ''),
  33: (64, 64, 95, '#2B2B2A', None, None, 'ALEFJÄLL, černá kůže', ''),
  116: (72, 77, 125, '#D5CFC8', None, None, 'VARPELEV, béžová síťovina', 'JYSK lists no height; 125 is read off the photo.'),
  209: (62, 60, 129, '#3A3A3A', None, None, 'MARKUS', 'Size taken from IKEA.'),
  210: (62, 60, 129, '#333333', None, None, 'MARKUS', 'Size taken from IKEA.'),
  # chairs: color = frame, color2 = seat
  34: (42, 49, 90, '#E3C29B', None, None, 'PINNTORP, borovice', ''),
  35: (46, 51, 80, '#E0C8A8', '#B9B7B2', None, 'LISABO, jasan', ''),
  36: (46, 55, 94, '#C9A57F', None, None, 'SKOGSTA, akácie', ''),
  37: (43, 49, 85, '#DDB78A', None, None, 'KARSKÄR, kaučukovník', ''),
  117: (42, 50, 86, '#E2C9A0', None, None, 'TYLSTRUP, borovice', ''),
  118: (45, 53, 87, '#C99F6D', '#8E8E92', None, 'JONSTRUP, šedá/dub', ''),
  # floor lamps: color = shade, color2 = pole/base; w = footprint, sw = shade width
  38: (62, 62, 151, '#EEEBE6', '#D9BD98', dict(shade='drum', base='tripod', sw=37), 'LAUTERS, jasan', ''),
  39: (34, 34, 181, '#4B4B4B', '#3A3A3A', dict(shade='dome', sw=32), 'HEKTAR, tmavě šedá', ''),
  40: (24, 24, 178, '#F2F2F0', '#1F1F1F', dict(shade='cone'), 'TÅGARP, černá/bílá', ''),
  41: (37, 37, 150, '#F1ECE4', '#DCC3A0', dict(shade='drum'), 'KINNAHULT, jasan', ''),
  123: (30, 30, 140, '#E6E0D8', '#D8D2CA', dict(shade='dome'), 'KENT, béžová', ''),
  124: (35, 35, 145, '#F0EEEA', '#B9BCBF', dict(shade='drum'), 'KRISTOF, ocel', ''),
  211: (35, 35, 130, '#F1EFEA', '#1E1E1E', dict(shade='drum'), 'SKAFTET + RINGSTA', 'Shade width read off the photo.'),
  212: (43, 43, 131.5, '#EDE9E2', '#8A5A35', dict(shade='drum'), 'Retro lampa, masiv/keramika', ''),
  # table lamps
  42: (25, 25, 24, '#F4F3EF', None, dict(shade='globe'), 'FADO, bílá', ''),
  43: (22, 22, 55, '#F2EFE8', '#B08D57', dict(shade='drum'), 'ÅRSTID, mosaz', ''),
  44: (30, 30, 50, '#E4DACB', '#E9E1D5', dict(shade='drum', base='vase'), 'BLIDVÄDER, keramika', ''),
  45: (18, 18, 30, '#F2F1EE', '#CFAE86', dict(shade='drum', base='tripod'), 'STORSEGEL, jasan', ''),
  125: (27, 27, 54, '#EAE3DA', '#2B2B2D', dict(shade='drum', base='vase'), 'JOACHIM, béžová/černá', ''),
  126: (19, 19, 25, '#B98A60', '#B98A60', dict(shade='drum', base='vase'), 'HANNIBAL, bambus', ''),
  213: (22, 22, 36, '#D2B083', None, dict(shade='globe'), 'MISTERHULT, bambus', ''),
  214: (27, 27, 36, '#F1EFEA', '#F1EFEA', dict(shade='dome', base='vase'), 'MARKUS (JYSK)', ''),
  # plants: w = leaf spread (IKEA gives only pot and height, so the spread is read off the photo)
  46: (60, 60, 140, '#4F6B3A', None, dict(pot=24, potc='#2B2B2B'), 'HOWEA, kentia', 'Leaf spread read off the photo.'),
  47: (60, 60, 140, '#557A3D', None, dict(pot=27, potc='#B5613F'), 'STRELITZIA', 'Leaf spread read off the photo.'),
  48: (55, 55, 170, '#6C8452', None, dict(pot=21, potc='#2B2B2B'), 'FEJKA fíkovník (umělý)', 'Leaf spread read off the photo.'),
  49: (25, 25, 40, '#4E6B3A', None, dict(pot=14, potc='#B5613F'), 'SANSEVIERIA', 'Leaf spread read off the photo.'),
  127: (65, 56, 150, '#8E9E6E', None, dict(pot=22, potc='#2B2B2B'), 'GUNNULF olivovník (umělý)', ''),
  # desks: legs = post | sled (U) | T | a | wood | panel; drawer = left | right | under
  50: (140, 80, 75, '#EFEFEA', '#E9E9E4', dict(build='desk', legs='a'), 'TROTTEN, bílá', ''),
  51: (140, 60, 73, '#E0CDB0', '#EFEFEA', dict(build='desk', legs='post', drawer='left'), 'LAGKAPTEN / ALEX, dub', ''),
  52: (140, 80, 75, '#C9A87C', '#3A3A3A', dict(build='desk', legs='sled'), 'SKÅLSTA, dub/U nohy', ''),
  53: (160, 80, 75, '#6E4F3E', '#3E3F41', dict(build='desk', legs='T'), 'IDÅSEN, hnědá', 'Height adjusts 65–79 cm.'),
  54: (140, 75, 75, '#CDAA82', '#CDAA82', dict(build='desk', legs='wood', drawer='under'), 'TONSTAD, dub', ''),
  113: (160, 80, 75, '#2A2A2B', '#1E1E1F', dict(build='desk', legs='T'), 'STAUNING, černá', ''),
  114: (130, 60, 75, '#C98E5E', '#C98E5E', dict(build='desk', legs='wood', drawer='under'), 'HAGE, dub', ''),
  115: (120, 60, 75, '#D5AF85', '#232323', dict(build='desk', legs='a'), 'SKOVLUNDE, dub/černá', ''),
  215: (155, 73, 74, '#C9A77E', '#D8B98E', dict(build='desk_trestle'), 'Dubová deska + ODDVALD kozy', 'Height estimated.'),
  216: (160, 80, 75, '#2A2A2B', '#1E1E1F', dict(build='desk', legs='T'), 'STAUNING (JYSK), černá', ''),
  217: (140, 65, 73, '#CDB08A', '#CDB08A', dict(build='desk', legs='panel', drawer='right'), 'MALM, dub', ''),
  # open shelves / bookcases
  55: (80, 28, 202, '#EEEEEA', None, dict(back=1), 'BILLY, bílá', ''),
  56: (89, 30, 179, '#DDBF95', None, dict(posts=1), 'IVAR + box, borovice', ''),
  57: (82, 37, 201, '#BF9C78', None, dict(back=1), 'TONSTAD, dub', ''),
  58: (78, 31, 171, '#D6B88C', None, dict(posts=1), 'HEJNE, smrk', ''),
  119: (80, 41, 183, '#C9AE78', None, dict(posts=1), 'LINDVED, dub', ''),
  120: (80, 40, 163, '#CFC3B0', '#1F1F1F', dict(posts=1), 'VANDBORG, dub/černá', ''),
  # bed benches: legs = panel | post | a
  59: (100, 28, 45, '#E2C39B', None, dict(legs='panel'), 'PERJOHAN, borovice', ''),
  60: (103, 36, 45, '#7A5A45', '#1F1F20', dict(legs='post'), 'ÅLHULT, hnědá/černá', ''),
  61: (78, 37, 47, '#B98A55', None, dict(legs='post', shelf=1), 'RÅGRUND, bambus', ''),
  62: (120, 46, 45, '#9A7452', '#222222', dict(legs='a', shelf=1), 'SKOGSTA, akácie', ''),
  128: (160, 35, 45, '#C3AA88', None, dict(legs='post'), 'ALSTED, dub', ''),
  129: (100, 36, 43, '#CFC6BB', '#C9A273', dict(legs='post', soft=1), 'HAGEBRO, pískový potah', ''),
  # wall shelves (h includes the bracket)
  63: (60, 17, 20, '#C5AC84', None, None, 'KLAVRESTRÖM, dub', ''),
  64: (59, 20, None, '#E3D4BD', None, None, 'BURHULT / SANDSHULT, osika', ''),
  65: (110, 26, 5, '#8A6450', None, None, 'LACK, ořech', ''),
  66: (101, 20, 21, '#6B4F3A', None, None, 'FJÄLLBO, černá', ''),
  130: (80, 24, 4, '#D4B997', None, None, 'ABILD, světlý dub', ''),
  131: (80, 24, 4, '#D1AE84', None, None, 'TERP, dub', ''),
  # rugs (the planner turns them to match the rug they replace)
  67: (170, 240, 1, '#D8CCBE', None, None, 'STOENSE, krémová', ''),
  68: (160, 230, 1, '#C4B393', None, None, 'TIOKRONA, přírodní', ''),
  69: (160, 230, 1, '#9E7F62', None, None, 'LOHALS, juta', ''),
  70: (170, 240, 1, '#9E998C', None, None, 'TIDTABELL, šedá', ''),
  71: (170, 240, 1, '#4F5966', None, None, 'LOKBYTE, tm. modrá', ''),
  132: (160, 230, 1, '#D6CBBD', None, None, 'LINGON, přírodní', ''),
  133: (160, 230, 1, '#C29E6E', None, None, 'MOGOP, juta', ''),
  134: (160, 230, 1, '#D5CFC0', None, None, 'LUCERNE, béžová', ''),
  222: (160, 230, 1, '#B7BBBE', None, None, 'Světle šedý se vzorem', ''),
  223: (200, 300, 1, '#E2DACB', None, None, 'Krémový, ručně tkaný', ''),
  # folding screens: color = frame, color2 = panels
  72: (150, None, 150, '#D9BD95', '#DDD3C3', dict(panels=3), 'GLAMBERGET, borovice', ''),
  73: (150, None, 175, '#333336', '#3D3D40', dict(panels=4), 'GRÅFJÄLLET, antracit', ''),
  74: (150, None, 170, '#D8B98E', '#E3CBA8', dict(panels=3), 'TOLKNING, ratan', ''),
  75: (216, None, 185, '#1F1F1F', '#F3F1EA', dict(panels=3), 'RISÖR, černá/bílá', ''),
  219: (216, None, 185, '#C9A57A', '#F1EBDD', dict(panels=3), 'RISÖR, přírodní', 'Size taken from IKEA.'),
  220: (172, None, 178, '#C9A57A', '#F1E9DA', dict(panels=4), 'Dřevěný paraván', ''),
  # slat dividers
  122: (90, 40, 182, '#D9BE94', None, None, 'EGTVED, bambus', 'Stands on feet 40 cm deep.'),
  221: (131, None, 260, '#EEEEEA', None, None, 'Lamelová stěna, bílá', 'Needs a ceiling pole to stand (the seller includes one).'),
  # curtain divider
  76: (None, None, None, '#E9E2D2', None, None, 'VIDGA stropní kolejnice (2)', 'Rail only, the curtains are extra.'),
}
CAT = {'bed', 'nightstand', 'dresser', 'wardrobe', 'kallax', 'armchair', 'coffee', 'office', 'chair', 'lamp', 'table_lamp', 'plant', 'desk', 'shelf', 'bedbench', 'wallshelf', 'rug', 'screen', 'slats', 'curtain_div'}
SHOP = lambda u: 'IKEA' if 'ikea.com' in u else 'JYSK' if 'jysk.cz' in u else 'Bazoš'
out = {}
for n, (w, d, h, c, c2, look, name, note) in P.items():
    r = src[n]; cat = r['cat']; assert cat in CAT, cat
    shop = SHOP(r['url'])
    img = r['img']  # small versions: the picker shows 44 px thumbnails
    if shop == 'IKEA': img += '?f=xxs'
    if shop == 'JYSK': img = img.replace('wd3.large', 'wd3.small')
    p = {'id': f'{shop.lower().replace("š", "s")}-{n}', 'shop': shop, 'name': name, 'price': round(r['price']) if r.get('price') else None,
         'url': r['url'], 'img': img}
    for k, v in (('w', w), ('d', d), ('h', h)):
        if v is not None: p[k] = v
    p['color'] = c
    if c2: p['color2'] = c2
    if look: p['look'] = look
    if shop == 'Bazoš': note = (f"{r['loc'].strip()}. " + note).strip()
    if note: p['note'] = note
    p['checked'] = '2026-09-29'
    out.setdefault(cat, []).append(p)
order = ['IKEA', 'JYSK', 'Bazoš']
for k in out: out[k].sort(key=lambda p: order.index(p['shop']))
js = '// Real products for the planner, one list per kind of piece. Generated from IKEA CZ, JYSK CZ and Bazoš (25 km around Prague) on 2026-09-29.\n'
js += '// w = along the front, d = front to back, h = height (cm). color/color2/look drive the 3D model. Missing w/d/h keep the size of the piece it replaces.\n'
js += 'window.PRODUCTS = {\n' + ''.join(f'  {k}: [\n' + ''.join('    ' + json.dumps(p, ensure_ascii=False) + ',\n' for p in v) + '  ],\n' for k, v in out.items()) + '};\n'
open(sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, '..', 'products.js'), 'w').write(js)
print({k: len(v) for k, v in out.items()}, sum(map(len, out.values())))
