# -*- coding: utf-8 -*-
import io, difflib

A = r'D:\codex\codex-data\youxi\编辑器原型\index.html'
B = r'D:\codex\codex-data\youxi\02-原型\_newver.html'

a = io.open(A, encoding='utf-8').read().split('\n')
b = io.open(B, encoding='utf-8').read().split('\n')
print('A lines=%d chars=%d' % (len(a), len(io.open(A, encoding='utf-8').read())))
print('B lines=%d chars=%d' % (len(b), len(io.open(B, encoding='utf-8').read())))

sm = difflib.SequenceMatcher(None, a, b)
opcodes = sm.get_opcodes()
print('--- diff blocks ---')
for tag, i1, i2, j1, j2 in opcodes:
    if tag == 'equal':
        continue
    print('%s A[%d:%d] -> B[%d:%d]  (A -%d / B +%d)' % (tag, i1 + 1, i2, j1 + 1, j2, i2 - i1, j2 - j1))
    for line in a[i1:i2][:4]:
        print('   - ' + line[:120])
    for line in b[j1:j2][:4]:
        print('   + ' + line[:120])
