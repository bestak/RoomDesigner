# START=301 python3 tools/details.py new.txt >> tools/data/extra.jsonl
# For each product URL in the file ("cat url" per line): name, price, W×D×H, image, dominant colours.
# Images go to tools/img/<n>.jpg (256 px, for looking at) and colours come from a 48 px BMP made by macOS sips.
import html, json, os, re, struct, subprocess, sys, urllib.request

UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 Chrome/130 Safari/537.36', 'Accept-Language': 'cs'}
get = lambda u: urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30).read()

def colours(path):
    """Most common non-background colours as hex, biggest cluster first."""
    bmp = path + '.bmp'
    subprocess.run(['sips', '-s', 'format', 'bmp', '-Z', '48', path, '--out', bmp], capture_output=True)
    b = open(bmp, 'rb').read()
    off, w, h, bpp = struct.unpack_from('<I', b, 10)[0], *struct.unpack_from('<ii', b, 18), struct.unpack_from('<H', b, 28)[0]
    step, row = bpp // 8, (w * bpp // 8 + 3) & ~3
    buckets = {}
    for y in range(abs(h)):
        for x in range(w):
            i = off + y * row + x * step
            B, G, R = b[i], b[i + 1], b[i + 2]
            if min(R, G, B) > 228 and max(R, G, B) - min(R, G, B) < 12: continue  # white / light grey backdrop
            k = (R // 24, G // 24, B // 24)
            s = buckets.setdefault(k, [0, 0, 0, 0]); s[0] += 1; s[1] += R; s[2] += G; s[3] += B
    top = sorted(buckets.values(), reverse=True)[:3]
    total = sum(v[0] for v in buckets.values()) or 1
    return [('#%02X%02X%02X' % (s[1] // s[0], s[2] // s[0], s[3] // s[0]), round(s[0] / total, 2)) for s in top]

def ikea(page):
    t = page.decode('utf-8', 'replace')
    name = html.unescape(re.search(r'<meta property="og:title" content="([^"]+)"', t).group(1))
    img = re.search(r'<meta property="og:image" content="([^"]+)"', t).group(1)
    price = re.search(r'"price":\["([\d.]+)"', t)
    dims = {}  # the product's own sizes ("name"/"measure"), not the package ones ("label"/"text")
    for m in re.findall(r'"measurements":(\[.*?\])', t):
        for x in json.loads(m):
            if 'name' in x: dims.setdefault(x['name'], x['measure'])
    return name, img, float(price.group(1)) if price else None, dims

def jysk(page):
    t = page.decode('utf-8', 'replace')
    name = html.unescape(re.search(r'<title>([^<|]+)', t).group(1).strip())
    img = re.search(r'<meta property="og:image" content="([^"]+)"', t).group(1)
    price = re.search(r'"price":"(\d+)', t)
    row = re.search(r'Rozměry po složení</th><td class="value">([^<]+)', t) or re.search(r'Rozměry</th><td class="value">([^<]+)', t)
    dims = dict(re.findall(r'([^:,]+):\s*([\d.,]+ ?c?m)', row.group(1))) if row else {}
    return name, img, float(price.group(1)) if price else None, {k.strip(): v for k, v in dims.items()}

IMG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')  # photos to look at; not committed
os.makedirs(IMG, exist_ok=True)
out = []
START = int(os.environ.get('START', 0))
for n, line in enumerate((l.split() for l in open(sys.argv[1] if len(sys.argv) > 1 else 'picks.txt') if l.strip() and not l.startswith('#')), START):
    cat, url = line[0], line[1]
    try:
        name, img, price, dims = (jysk if 'jysk.cz' in url else ikea)(get(url))
        path = os.path.join(IMG, f'{n}.jpg')
        open(path, 'wb').write(get(img))
        subprocess.run(['sips', '-Z', '256', path], capture_output=True)
        out.append(dict(n=n, cat=cat, name=name, price=price, dims=dims, url=url, img=img, colours=colours(path)))
    except Exception as e:
        out.append(dict(n=n, cat=cat, url=url, error=repr(e)))
    print(json.dumps(out[-1], ensure_ascii=False), flush=True)
