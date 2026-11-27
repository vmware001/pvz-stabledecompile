import struct, os, io
SRC = r"D:\data\code\pvz\.trash\pak_backup\main.pak.src.orig"
raw = open(SRC, 'rb').read()
dec = bytes(b ^ 0xF7 for b in raw)
magic, version = struct.unpack_from('<II', dec, 0)
assert magic == 0xBAC04AC0 and version == 0, (hex(magic), version)
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
dir_end = pos
data_pos = dir_end
for e in entries:
    e['data'] = dec[data_pos:data_pos + e['size']]
    data_pos += e['size']
print('entries:', len(entries), 'dir_end:', dir_end, 'data_end:', data_pos, 'file size:', len(dec))
# rebuild
out = bytearray()
out += struct.pack('<II', magic, version)
for e in entries:
    out.append(e['flags'])
    out.append(len(e['name']))
    out += e['name']
    out += struct.pack('<i', e['size'])
    out += e['ft']
out.append(0x80)
for e in entries:
    out += e['data']
print('rebuilt size:', len(out), 'identical:', bytes(out) == dec)
if bytes(out) != dec:
    for i in range(min(len(out), len(dec))):
        if out[i] != dec[i]:
            print('first diff at', i, dec[max(0,i-20):i+20], out[max(0,i-20):i+20]); break
# 保存解码流供后续使用(pickle)
import pickle
pickle.dump(entries, open(r'D:\data\code\pvz\.trash\pak_entries2.pkl', 'wb'))
print('saved entries pickle')
