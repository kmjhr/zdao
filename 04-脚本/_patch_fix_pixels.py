# -*- coding: utf-8 -*-
import io, sys

P = r'D:\codex\codex-data\youxi\02-原型\_newver.html'
src = io.open(P, 'r', encoding='utf-8').read()
edits = []

a = '''  pushUndo();
  var out = makeEmptyPixels(n);
  for (var y = 0; y < n; y++) {
    for (var x = 0; x < n; x++) {
      var c = l.pixels[y * n + x];'''
r = '''  pushUndo();
  var out = makeEmptyPixels(n * n);
  for (var y = 0; y < n; y++) {
    for (var x = 0; x < n; x++) {
      var c = l.pixels[y * n + x];'''
edits.append((a, r, 'nudgeLayer'))

a = '''  pushUndo();
  var out = makeEmptyPixels(n);
  for (var y = 0; y < n; y++) {
    for (var x = 0; x < n; x++) out[y * n + (n - 1 - x)] = l.pixels[y * n + x];'''
r = '''  pushUndo();
  var out = makeEmptyPixels(n * n);
  for (var y = 0; y < n; y++) {
    for (var x = 0; x < n; x++) out[y * n + (n - 1 - x)] = l.pixels[y * n + x];'''
edits.append((a, r, 'mirrorCurrentLayer'))

a = '    var flip = makeEmptyPixels(n);'
r = '    var flip = makeEmptyPixels(n * n);'
edits.append((a, r, 'duplicateLayer'))

for a, r, label in edits:
    c = src.count(a)
    if c != 1:
        print('FAIL %s: count=%d' % (label, c))
        sys.exit(1)
    print('OK %s' % label)

out = src
for a, r, label in edits:
    out = out.replace(a, r, 1)

io.open(P, 'w', encoding='utf-8', newline='\n').write(out)
print('WROTE chars=%d' % len(out))
