# KuKi Design System

Kuki is an intelligent health companion app for your furbabies :)

Design system for **KuKi**. Lives in two places, kept in sync:

- **Figma**: [KuKi Design System](https://www.figma.com/design/lk7PRy9xnmLg1caaio6ROS/KuKi-Design-System) — variables, text styles, and the full component library.
- **Code**: this folder — token source of truth, CSS custom properties, and React components.

## Brand

Derived from the KuKi logo and login screen:

| Role | Color | Source |
| --- | --- | --- |
| Brand (terracotta) | `#DA7F44` (ramp 50–950) | logo fur / login link orange |
| Accent (golden cream) | `#F5C563` / `#F8D890` | logo background |
| Ink (chocolate) | `#2B1708`–`#1F1004` | wordmark; replaces pure black for high-emphasis surfaces (FAB, filled controls) |
| Neutrals | `#F9F9F9`–`#101010` | greys already shipped in the app screens |

**Wellness status semantics** (the five streak states):

| Token | Meaning | Hue |
| --- | --- | --- |
| `status-none` | no data yet (new user) | blue |
| `status-critical` | severe symptom / seizure today | red |
| `status-caution` | 1–3 symptom-free days | amber |
| `status-good` | 4–7 symptom-free days | light green (lime) |
| `status-excellent` | 8+ symptom-free days | dark green |

Metric category colors: weight=turquoise, vaccine=pink, activity=blue, nutrition=lime,
sleep=violet, medication=green — all with light/dark variants.

## Layout

```
tokens/
  generate_tokens.py   ← EDIT THIS to change any token, then run it
  tokens.json          generated — full token tree (consume from Android/iOS)
  figma-vars.json      generated — flat lists used by the Figma import scripts
  css/tokens.css       generated — CSS custom properties, light + dark
react/
  src/                 typed React components (Button, IconButton, Badge, Chip,
                       WellnessCard, MetricCard, SectionHeader, ListRow, Avatar,
                       TopNav, BottomBar, AIOrb) — `npm run typecheck` passes
  styles/components.css
assets/
  ai-sparkle-animated.svg  KuKi's real animated Pet AI sparkle burst
preview/
  index.html           tabbed reference site (Overview/Color/Typography/Icons/
                       Buttons/Badges & Chips/Cards/Navigation/Pet AI)
  squircle.js           corner-smoothing clip-path utility (see Rule 6)
  ai-orb.js              inlines + uniquifies the sparkle SVG per orb (see Rule 7)
```

Preview locally:

```sh
cd kuki-design-system && python3 -m http.server 8321
# open http://localhost:8321/preview/index.html — sidebar tabs, dark-mode toggle bottom-left
```

## Rules

1. `generate_tokens.py` is the **only** place token values change. It asserts WCAG AA contrast
   on every meaningful pairing and fails the build if a ramp regresses.
2. Components consume **semantic** tokens (`--kuki-sem-*`) only; primitives are for the
   semantic layer to alias.
3. Dark mode flips `text/on-brand`, `text/on-status`, and `icon/on-brand` to chocolate ink
   because brand/status surfaces get *lighter* in dark mode.
4. Buttons are pills (`radius/control` → 9999). Cards are `radius/container` (32).
   Small badges are `radius/badge` (6).
5. Typography is **Google Sans Flex only** (weights ExtraLight→Bold). The Figma file currently
   renders text styles in Inter because Figma's font service doesn't list Google Sans Flex
   (the font IS installed on this machine — browsers use it). Once it appears in Figma's font
   menu, run the swap script in `figma-font-swap.md`.
6. Cards get Figma's native `cornerSmoothing` (0.6, applied file-wide to every radius'd frame).
   CSS has no equivalent, so `preview/squircle.js` clips each `[data-squircle="RADIUS"]` element
   to a true superellipse (Lamé curve, exponent 2–5 mapped from smoothing 0–1) via `clip-path`.
7. The wellness-card gradient is centered (`radial-gradient(100% 100% at 50% 50%, …)` in
   `tokens.css`; identity transform in Figma) so the pastel edge color reaches all four corners
   symmetrically — never re-introduce an off-center `at X% Y%` or Figma `gradientTransform`.
8. The Pet AI orb's sparkle is KuKi's real animated SVG. It must be **inlined**, never loaded via
   `<img>` — browsers don't run an `<img>`-embedded SVG's own CSS `@keyframes`, and this asset's
   sparkles start every loop at `opacity:0`, so an `<img>` copy renders permanently blank.
   `preview/ai-orb.js` (web) and `AIOrb.tsx` (React) both fetch the asset once and inline a
   copy with every id/keyframe-name uniquified per instance, so multiple orbs on one page don't
   collide. The background swirl is a separate, pure-CSS shader approximation (blurred rotating
   conic gradient, screen-blended).

## Known deviations / notes

- Figma semantic typography variables were folded into the text styles themselves
  (size/line-height/tracking are variable-bound; family/weight will be bound after the font swap).
- The Top Nav pill background is `neutral/950 @ 8%` as a raw paint in Figma — variable-bound
  translucent fills rendered unreliably.
- **Figma mode gotcha**: this file's image-export/render pipeline does not reliably default to
  the `light` mode a plugin session reports as default — pages were pinned explicitly
  (`page.setExplicitVariableModeForCollection(semanticColorCollection, lightModeId)`) to get
  deterministic light rendering. If a new page ever renders unexpectedly dark, pin it the same way
  rather than assuming the token values are wrong.
