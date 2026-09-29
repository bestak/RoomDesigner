# Dump IKEA CZ search candidates per category: python3 ikea_search.py > cands.txt
import json, sys, urllib.parse, urllib.request

Q = {
    'bed': ['postel 90x200'],
    'nightstand': ['noční stolek'],
    'dresser': ['komoda 3 zásuvky', 'komoda'],
    'wardrobe': ['šatní skříň'],
    'kallax': ['kallax policový díl'],
    'armchair': ['křeslo'],
    'coffee': ['konferenční stolek', 'odkládací stolek'],
    'office': ['kancelářská židle'],
    'chair': ['židle dřevo'],
    'lamp': ['stojací lampa'],
    'table_lamp': ['stolní lampa'],
    'plant': ['umělá rostlina', 'rostlina v květináči'],
    'desk': ['psací stůl', 'kozy stůl', 'stolní deska'],
    'shelf': ['knihovna', 'regál'],
    'bedbench': ['lavice'],
    'wallshelf': ['nástěnná police'],
    'rug': ['koberec 170x240', 'koberec 160x230', 'koberec 133x195'],
    'screen': ['paraván', 'dělicí stěna'],
    'curtain_div': ['stropní kolejnice závěs'],
    'bench': ['klavírní stolička', 'stolička'],
}
cats = sys.argv[1:] or list(Q)
for cat in cats:
    for q in Q[cat]:
        url = 'https://sik.search.blue.cdtapps.com/cz/cs/search-result-page?' + urllib.parse.urlencode({'q': q, 'size': 24, 'types': 'PRODUCT'})
        d = json.load(urllib.request.urlopen(url, timeout=20))
        print(f'## {cat} · {q}')
        for i in d['searchResultPage']['products']['main']['items']:
            p = i['product']
            print(' ', p['id'], '|', p['name'], '|', p['typeName'], '|', p.get('itemMeasureReferenceText'), '|', p['salesPrice'].get('numeral'), '|', p.get('validDesignText') or '', '|', p['pipUrl'].split('/p/')[1])
