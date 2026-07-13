# Swapping Figma text to Google Sans Flex

The design system's text styles currently render in **Inter** because Figma's font list does
not expose Google Sans Flex in this environment (macOS has the font — the web preview uses it).

**When Google Sans Flex shows up in Figma's font picker** (install it system-wide from
fonts.google.com and restart the Figma desktop app), ask Claude to run this against the
KuKi Design System file, or paste it into any plugin console:

```js
const MAP = { 'Extra Light':'ExtraLight', 'Light':'Light', 'Regular':'Regular',
              'Medium':'Medium', 'Semi Bold':'SemiBold', 'Bold':'Bold' };
const FAM = 'Google Sans Flex';
for (const style of Object.values(MAP)) await figma.loadFontAsync({ family: FAM, style });
// 1. text styles
for (const s of await figma.getLocalTextStylesAsync()) {
  if (s.fontName.family === 'Inter') s.fontName = { family: FAM, style: MAP[s.fontName.style] };
}
// 2. any text node still on Inter
for (const page of figma.root.children) {
  await page.loadAsync();
  for (const t of page.findAllWithCriteria({ types: ['TEXT'] })) {
    if (t.fontName !== figma.mixed && t.fontName.family === 'Inter') {
      t.fontName = { family: FAM, style: MAP[t.fontName.style] ?? 'Regular' };
    }
  }
}
// 3. bind family/style variables on the text styles (primitives.typography)
```

Then bind `font-family/default` and the `font-style/*` variables to each text style so the
styles stay token-driven.
