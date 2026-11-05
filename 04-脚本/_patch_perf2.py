# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()

a = '''    saved_at: savedAt
  });
  draftSaveTimer = null;'''
r = '''    saved_at: savedAt
  });
  if (draftSaveTimer) { clearTimeout(draftSaveTimer); draftSaveTimer = null; }'''

if src.count(a) != 1:
    print('FAIL')
    sys.exit(1)
out = src.replace(a, r, 1)
io.open(P, 'w', encoding='utf-8', newline='\n').write(out)
print('OK timer clear')
