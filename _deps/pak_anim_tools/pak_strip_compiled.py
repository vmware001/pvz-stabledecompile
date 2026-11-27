import struct, os
SRC = r"D:\data\code\pvz\.trash\pak_backup\main.pak.bin.orig"
raw = open(SRC, 'rb').read()
dec = bytes(b ^ 0xF7 for b in raw)
magic, version = struct.unpack_from('<II', dec, 0)
assert magic == 0xBAC04AC0
pos = 8
entries = []
while True:
    flags = dec[pos]; pos += 1
    if flags & 0x80:
        break
    nlen = dec[pos]; pos += 1
    name = dec[pos:pos+nlen]; pos += nlen
    size = struct.unpack_from('<i', dec, pos)[0]; pos += 4
    ft = dec[pos:pos+8]; pos += 8
    entries.append({'flags': flags, 'name': name, 'size': size, 'ft': ft, 'data': None})
dend = pos
dp = dend
for e in entries:
    e['data'] = dec[dp:dp+e['size']]
    dp += e['size']
print('total entries:', len(entries))
targets = [b'zombie_football.reanim.compiled', b'zombie_ladder.reanim.compiled', b'zombie_yeti.reanim.compiled',
           b'zombie_jackbox.reanim.compiled', b'zombie_disco.reanim.compiled', b'zombie_newspaper.reanim.compiled']
def is_target(name):
    low = name.lower()
    return low.startswith(b'compiled\\reanim\\') and any(t in low for t in targets)
kept = [e for e in entries if not is_target(e['name'])]
removed = [e['name'].decode('latin-1') for e in entries if is_target(e['name'])]
print('removed:', removed)
out = bytearray()
out += struct.pack('<II', magic, version)
for e in kept:
    out.append(e['flags']); out.append(len(e['name'])); out += e['name']
    out += struct.pack('<i', e['size']); out += e['ft']
out.append(0x80)
for e in kept:
    out += e['data']
enc = bytes(b ^ 0xF7 for b in bytes(out))
dst = r"D:\data\code\pvz\stabledecompile\build\DebugGOTY_Win32\bin\main.pak"
open(dst, 'wb').write(enc)
print('wrote', dst, 'size', len(enc))
