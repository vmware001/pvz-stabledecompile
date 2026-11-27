import struct, re, math

SRC = r"D:\data\code\pvz\.trash\pak_backup\main.pak.src.orig"
dec = bytes(b ^ 0xF7 for b in open(SRC,'rb').read())
magic, version = struct.unpack_from('<II', dec, 0)
pos = 8
entries = []
while True:
    flags = dec[pos]; pos += 1
    if flags & 0x80: break
    nlen = dec[pos]; pos += 1
    name = dec[pos:pos+nlen]; pos += nlen
    size = struct.unpack_from('<i', dec, pos)[0]; pos += 4
    ft = dec[pos:pos+8]; pos += 8
    entries.append({'flags': flags, 'name': name, 'size': size, 'ft': ft, 'data': None})
dend = pos; dp = dend
for e in entries:
    e['data'] = dec[dp:dp+e['size']]; dp += e['size']

TARGETS = ['zombie_newspaper','zombie_football','zombie_ladder','zombie_yeti','zombie_jackbox','zombie_disco']
COSMETIC = ('head1','head2','hair','cone','bucket','tongue','screendoor','anim_walk2','anim_idle2','anim_death2')

def parse_tracks(txt):
    out = []
    for m in re.finditer(r'<track>(.*?)</track>', txt, re.S):
        body = m.group(1)
        nm = re.search(r'<name>(.*?)</name>', body, re.S).group(1)
        ts = re.findall(r'<t>(.*?)</t>', body, re.S)
        out.append([nm, ts, m.group(0)])
    return out

def getf(c, tag):
    m = re.search(r'<%s>([-\d.]+)</%s>' % (tag, tag), c)
    return float(m.group(1)) if m else None

def fmt(c, x, y, kx, ky, sx, sy, img):
    s = '<t>'
    for tago, val in (('x',x),('y',y),('kx',kx),('ky',ky),('sx',sx),('sy',sy)):
        if val is not None:
            s += '<%s>%s</%s>' % (tago, round(val,3), tago)
    if img: s += '<i>%s</i>' % img
    return s + '</t>'

def modify(txt):
    tracks = parse_tracks(txt)
    anim_tracks = [(nm, ts) for nm, ts, _ in tracks if nm.startswith('anim_') and not any(c in nm for c in COSMETIC)]
    bounds = set()
    for nm, ts in anim_tracks:
        for i,c in enumerate(ts):
            if c.strip(): bounds.add(i)
    bounds = sorted(bounds)
    # 选 idle 段; 没有 idle 就用 moonwalk/dance
    pick = None
    for cand in ('anim_idle','anim_moonwalk','anim_dance','anim_point'):
        for nm, ts in anim_tracks:
            if nm == cand:
                start = next(i for i,c in enumerate(ts) if c.strip())
                ends = [b for b in bounds if b > start]
                end = min(ends) if ends else len(ts)
                if end - start >= 10:
                    pick = (cand, start, end)
                break
        if pick: break
    if pick is None:
        return None, 'no suitable segment'
    cand, start, end = pick
    seg = end - start
    out_tracks = []
    renamed = False
    for nm, ts, raw in tracks:
        if nm == cand and not renamed:
            out_tracks.append(raw.replace('<name>%s</name>' % nm, '<name>anim_swim</name>', 1))
            renamed = True
            continue
        low = nm.lower()
        newts = list(ts)
        for k in range(seg):
            idx = start + k
            c = ts[idx] if idx < len(ts) else ''
            if not c.strip(): continue
            x, y = getf(c,'x'), getf(c,'y')
            kx, ky = getf(c,'kx'), getf(c,'ky')
            sx, sy = getf(c,'sx'), getf(c,'sy')
            img = re.search(r'<i>([^<]+)</i>', c)
            ph = 2.0*math.pi*k/seg
            if 'ground' in low or 'root' in low:
                if y is not None: y += 3.0*math.sin(ph)
            elif 'leg' in low or 'foot' in low:
                side = 1.0 if 'left' in low else -1.0
                if ky is not None: ky += side*16.0*math.sin(ph) + 8.0
                if y is not None: y += side*3.5*math.sin(ph)
            elif 'arm' in low or 'hand' in low:
                side = 1.0 if 'left' in low else -1.0
                if ky is not None: ky += side*12.0*math.sin(ph+1.5) - 6.0
            else:
                if ky is not None: ky += 10.0
                if y is not None: y += 3.0 + 2.0*math.sin(ph)
            newts[idx] = fmt(c, x, y, kx, ky, sx, sy, img.group(1) if img else None)
        if newts != ts:
            head = raw.split('<t>')[0]
            body = ''
            for c in newts:
                body += c if c.startswith('<t>') else ('<t>' + c + '</t>')
            out_tracks.append(head + body + '</track>')
        else:
            out_tracks.append(raw)
    head = txt.split('<track>')[0]
    new_txt = head + '\n'.join(out_tracks) + '\n'
    return new_txt, '%s seg %d..%d (len %d)' % (cand, start, end-1, seg)

for e in entries:
    low = e['name'].lower()
    if not (low.startswith(b'reanim\\') and low.endswith(b'.reanim')): continue
    base = low[len(b'reanim\\'):-len(b'.reanim')].decode('latin-1')
    if base not in TARGETS: continue
    txt = e['data'].decode('latin-1')
    new_txt, info = modify(txt)
    if new_txt is None:
        print('SKIP', base, info); continue
    e['data'] = new_txt.encode('latin-1'); e['size'] = len(e['data'])
    print('OK', base, info, '| anim_swim count', new_txt.count('anim_swim'))

def is_compiled(name):
    low = name.lower()
    if not low.startswith(b'compiled\\reanim\\') or not low.endswith(b'.reanim.compiled'): return False
    stem = low[len(b'compiled\\reanim\\'):-len(b'.reanim.compiled')].decode('latin-1')
    return stem in TARGETS
kept = [x for x in entries if not is_compiled(x['name'])]
print('removed compiled:', len(entries)-len(kept))
out = bytearray()
out += struct.pack('<II', magic, version)
for x in kept:
    out.append(x['flags']); out.append(len(x['name'])); out += x['name']
    out += struct.pack('<i', x['size']); out += x['ft']
out.append(0x80)
for x in kept: out += x['data']
open(r"D:\data\code\pvz\.trash\main_swim.pak",'wb').write(bytes(b ^ 0xF7 for b in bytes(out)))
print('wrote main_swim.pak', len(out))
