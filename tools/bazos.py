# Bazoš furniture listings within 25 km of Prague: python3 bazos.py > bazos.txt
import html, json, re, urllib.parse, urllib.request

Q = {
    'bed': ['postel 90x200'], 'nightstand': ['noční stolek'], 'dresser': ['komoda dub', 'komoda ikea'],
    'wardrobe': ['šatní skříň 120'], 'kallax': ['kallax 5x5', 'kallax 4x4'], 'armchair': ['poäng', 'strandmon', 'křeslo dub'],
    'coffee': ['konferenční stolek kulatý'], 'office': ['kancelářská židle markus', 'kancelářská židle'], 'chair': ['židle dřevěná'],
    'lamp': ['stojací lampa'], 'table_lamp': ['stolní lampa'], 'desk': ['psací stůl dub', 'psací stůl 160'],
    'shelf': ['knihovna billy', 'regál ivar'], 'bedbench': ['lavice dřevěná'], 'screen': ['paraván'], 'slats': ['lamelová stěna', 'dělicí stěna'],
    'rug': ['koberec 160x230', 'koberec 200x300'], 'plant': ['monstera velká', 'fíkus'], 'wallshelf': ['nástěnná police dub'],
}
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh) AppleWebKit/537.36 Chrome/130 Safari/537.36'}
out = []
for cat, qs in Q.items():
    for q in qs:
        u = 'https://nabytek.bazos.cz/?' + urllib.parse.urlencode({'hledat': q, 'hlokalita': '11000', 'humkreis': '25'})
        t = urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read().decode('utf-8', 'replace')
        for b in t.split('<div class="inzeraty inzeratyflex">')[1:]:
            m = re.search(r'href="(/inzerat/[^"]+)"><img src="([^"]+)"[^>]*alt="([^"]*)"', b)
            if not m: continue
            desc = re.sub(r'<[^>]+>|\s+', ' ', html.unescape(re.search(r'<div class=popis>(.*?)</div>', b, re.S).group(1))).strip()
            price = re.sub(r'\D', '', re.search(r'<div class="inzeratycena"><b>(.*?)</b>', b, re.S).group(1))
            loc = re.sub(r'<br>', ' ', re.search(r'<div class="inzeratylok">(.*?)</div>', b, re.S).group(1))
            out.append(dict(cat=cat, q=q, url='https://nabytek.bazos.cz' + m.group(1), img=m.group(2), title=html.unescape(m.group(3)), price=int(price) if price else None, loc=loc, desc=desc))
for o in out: print(json.dumps(o, ensure_ascii=False))
