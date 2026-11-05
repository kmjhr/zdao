# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()

a = '.draft-thumb{width:100%;aspect-ratio:1;image-rendering:pixelated;background:#fff;border:1px solid #E4E3DD;display:block}'
r = '.draft-thumb{width:100%;height:96px;object-fit:contain;image-rendering:pixelated;background:#fff;border:1px solid #E4E3DD;display:block}'

if src.count(a) != 1:
    print('FAIL thumb css')
    sys.exit(1)
out = src.replace(a, r, 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(out)
print('OK thumb css fixed')
