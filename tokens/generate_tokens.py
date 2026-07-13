#!/usr/bin/env python3
"""KuKi Design System — token generator.

Source of truth for all design tokens. Emits:
  - tokens.json        (full token tree: primitives + semantic light/dark)
  - css/tokens.css     (CSS custom properties, light + dark)
  - figma-vars.json    (flat lists consumed by the Figma import scripts)

Brand anchors extracted from the KuKi Figma sources:
  logo fur / UI orange  #DA7F44   logo cream #F8D890  logo gold #F5C563
  brown text #623414    wordmark ink ~#241205
  link blue #196FE0     critical red #CD0202 / #AB0202 / pastel #FAE5E5
  lime #54AF00/#46710F  green #00960B/#005807  amber #F58805
  metric pastels: turquoise #CCF3F6, pink #F6CCF2, blue #CCDFF9,
                  lime #E1EED1, violet #EFE5FB, green #CCEDE6
"""
import json, os

# ---------- color math ----------
def srgb_to_lin(c):
    c /= 255.0
    return c / 12.92 if c <= 0.04045 * 255 / 255 else ((c + 0.055) / 1.055) ** 2.4

def luminance(hexc):
    h = hexc.lstrip('#')
    r, g, b = (int(h[i:i+2], 16) for i in (0, 2, 4))
    return 0.2126 * srgb_to_lin(r) + 0.7152 * srgb_to_lin(g) + 0.0722 * srgb_to_lin(b)

def contrast(a, b):
    la, lb = luminance(a), luminance(b)
    lo, hi = min(la, lb), max(la, lb)
    return (hi + 0.05) / (lo + 0.05)

WHITE, BLACK = '#FFFFFF', '#101010'

# ---------- primitive ramps (hand-tuned, contrast-asserted below) ----------
RAMPS = {
    'neutral': {  # matches greys already shipped in the app screens
        '50': '#F9F9F9', '100': '#F3F3F3', '200': '#E4E4E4', '300': '#CFCFCF',
        '400': '#9F9F9F', '500': '#8A8A8A', '600': '#666666', '700': '#4F4F4F',
        '800': '#404040', '900': '#1A1A1A', '950': '#101010',
    },
    'brand': {  # KuKi terracotta orange — anchor 500 = login/logo orange
        '50': '#FBF3ED', '100': '#F7E5D7', '200': '#F0CDB2', '300': '#E8B189',
        '400': '#E19864', '500': '#DA7F44', '600': '#B25A20', '700': '#96491A',
        '800': '#7B3E18', '900': '#623414', '950': '#401F0C',
    },
    'accent': {  # golden cream from the logo
        '50': '#FEFBF2', '100': '#FDF4DE', '200': '#FAE7B8', '300': '#F8D890',
        '400': '#F5C563', '500': '#EFAF35', '600': '#C98812', '700': '#A16C0E',
        '800': '#7E5510', '900': '#5C3E0D', '950': '#3B2808',
    },
    'chocolate': {  # warm ink from the wordmark — replaces pure black emphasis
        '600': '#623C1E', '700': '#4E2E15', '800': '#3A2210',
        '900': '#2B1708', '950': '#1F1004',
    },
    'red': {  # status: critical — anchors #CD0202 / #AB0202 / #FAE5E5
        '50': '#FDF0F0', '100': '#FAE5E5', '200': '#F5C4C4', '300': '#EE9494',
        '400': '#E35151', '500': '#CD0202', '600': '#AB0202', '700': '#8C0202',
        '800': '#700202', '900': '#570202', '950': '#3A0101',
    },
    'amber': {  # status: caution — anchor gradient orange #F58805
        '50': '#FFF8E7', '100': '#FFEFC7', '200': '#FFE28F', '300': '#FFD666',
        '400': '#FBAE1F', '500': '#F58805', '600': '#CE6E04', '700': '#9E5303',
        '800': '#7E4302', '900': '#5C3102', '950': '#3B1F01',
    },
    'lime': {  # status: good — anchors #54AF00 / #46710F / #E1EED1
        '50': '#F4F9EC', '100': '#E1EED1', '200': '#C8E3A4', '300': '#A4D162',
        '400': '#7FC916', '500': '#54AF00', '600': '#4A9203', '700': '#46710F',
        '800': '#375A0C', '900': '#2A4409', '950': '#1B2C06',
    },
    'green': {  # status: excellent — anchors #00960B / #007D09 / #005807
        '50': '#E9F7EA', '100': '#CFEDD1', '200': '#A3DDA8', '300': '#6FC876',
        '400': '#34AD3E', '500': '#00960B', '600': '#007D09', '700': '#036707',
        '800': '#005807', '900': '#084409', '950': '#062D06',
    },
    'blue': {  # status: none/info — anchors link #196FE0 / #004195 / #CCDFF9
        '50': '#EEF5FD', '100': '#CCDFF9', '200': '#A3C7F4', '300': '#6FA6ED',
        '400': '#3E88E7', '500': '#196FE0', '600': '#1259B8', '700': '#0C4694',
        '800': '#004195', '900': '#0A3068', '950': '#071E40',
    },
}

# supplementary category palette (metric chips, data viz) — 5 steps each
EXTENDED = {
    'turquoise': {'100': '#CCF3F6', '300': '#7ADEE7', '500': '#00AEBD', '700': '#00838C', '900': '#00494E'},
    'pink':      {'100': '#F6CCF2', '300': '#EC8AE2', '500': '#D200BD', '700': '#8C007E', '900': '#4E0046'},
    'violet':    {'100': '#EFE5FB', '300': '#C9A5F2', '500': '#8A3FE8', '700': '#3D008C', '900': '#26005C'},
}

BASE = {'white': '#FFFFFF', 'black': '#101010', 'transparent': 'rgba(0,0,0,0)'}

# wellness gradients (kept as component-level recipes, not variables)
GRADIENTS = {
    'wellness/none':      ['#3CC4FF', '#2CCAFF', '#55CCFF', '#D6E9F5'],
    'wellness/critical':  ['#FF3C3F', '#FF4F2C', '#FF8555', '#F5D6DC'],
    'wellness/caution':   ['#FFCE09', '#F58805', '#F1944D', '#CFCBD5'],
    'wellness/good':      ['#06AC00', '#54AF00', '#7FC916', '#FFC93C'],
    'wellness/excellent': ['#005807', '#007D09', '#00960B', '#5ABB01'],
    'ai-orb':             ['#A7F5FF', '#00138F', '#000000'],
}

# ---------- contrast assertions (WCAG AA) ----------
checks = [
    # (fg, bg, min_ratio, label)
    (WHITE, RAMPS['brand']['600'], 4.5, 'white on brand/600 (primary button)'),
    (WHITE, RAMPS['red']['500'], 4.5, 'white on red/500 (critical button)'),
    (RAMPS['brand']['700'], '#FFFFFF', 4.5, 'brand/700 text on white'),
    (RAMPS['brand']['900'], RAMPS['brand']['50'], 4.5, 'brand/900 on brand/50 (subtle chip)'),
    (RAMPS['red']['600'], RAMPS['red']['100'], 4.5, 'red/600 on red/100'),
    (RAMPS['amber']['700'], RAMPS['amber']['100'], 4.5, 'amber/700 on amber/100'),
    (RAMPS['lime']['700'], RAMPS['lime']['100'], 4.5, 'lime/700 on lime/100'),
    (RAMPS['green']['700'], RAMPS['green']['100'], 4.5, 'green/700 on green/100'),
    (RAMPS['blue']['600'], RAMPS['blue']['100'], 4.5, 'blue/600 on blue/100'),
    (RAMPS['blue']['500'], '#FFFFFF', 4.5, 'link blue on white'),
    (RAMPS['neutral']['600'], '#FFFFFF', 4.5, 'neutral/600 subtle text on white'),
    (RAMPS['neutral']['900'], RAMPS['neutral']['100'], 4.5, 'text on canvas'),
    ('#F9F9F9', '#1C1A18', 4.5, 'dark mode text on card'),
    (WHITE, RAMPS['chocolate']['900'], 4.5, 'white on chocolate/900 (FAB)'),
    (RAMPS['chocolate']['950'], RAMPS['brand']['500'], 4.5, 'dark-mode on-brand ink on brand/500'),
    (RAMPS['chocolate']['950'], RAMPS['red']['400'], 4.5, 'dark-mode on-status ink on red/400'),
    (RAMPS['chocolate']['950'], RAMPS['lime']['400'], 4.5, 'dark-mode on-status ink on lime/400'),
]

def run_checks():
    failed = []
    for fg, bg, need, label in checks:
        r = contrast(fg, bg)
        status = 'PASS' if r >= need else 'FAIL'
        if r < need:
            failed.append((label, r))
        print(f'  {status}  {r:5.2f}:1  (need {need})  {label}')
    return failed

# ---------- semantic tokens: {name: {light: ref|hex, dark: ref|hex}} ----------
# refs are 'ramp/step' strings resolved against RAMPS/EXTENDED/BASE
def R(ref): return ref  # readability marker

SEMANTIC_COLOR = {
    # SURFACE
    'surface/canvas':              {'light': 'neutral/100', 'dark': '#121110'},
    'surface/default':             {'light': 'white',       'dark': '#1C1A18'},
    'surface/raised':              {'light': 'white',       'dark': '#26231F'},
    'surface/sunken':              {'light': 'neutral/200', 'dark': '#0C0B0A'},
    'surface/overlay':             {'light': '#101010',     'dark': '#000000'},  # use w/ opacity/overlay
    'surface/brand':               {'light': 'brand/600',   'dark': 'brand/500'},
    'surface/brand-hover':         {'light': 'brand/700',   'dark': 'brand/400'},
    'surface/brand-pressed':       {'light': 'brand/800',   'dark': 'brand/300'},
    'surface/brand-subtle':        {'light': 'brand/50',    'dark': '#33221A'},
    'surface/brand-subtle-hover':  {'light': 'brand/100',   'dark': '#3E2A1F'},
    'surface/brand-subtle-pressed':{'light': 'brand/200',   'dark': '#4A3225'},
    'surface/accent':              {'light': 'accent/400',  'dark': 'accent/400'},
    'surface/accent-subtle':       {'light': 'accent/100',  'dark': '#332B14'},
    'surface/emphasis':            {'light': 'chocolate/900', 'dark': 'neutral/100'},  # FAB & high-emphasis
    'surface/emphasis-hover':      {'light': 'chocolate/800', 'dark': 'neutral/200'},
    'surface/emphasis-pressed':    {'light': 'chocolate/700', 'dark': 'neutral/300'},
    'surface/selected':            {'light': 'brand/100',   'dark': '#3E2A1F'},
    'surface/disabled':            {'light': 'neutral/200', 'dark': '#2E2B28'},
    # STATUS SURFACES
    'surface/status-none':         {'light': 'blue/500',    'dark': 'blue/400'},
    'surface/status-none-subtle':  {'light': 'blue/100',    'dark': '#152438'},
    'surface/status-critical':     {'light': 'red/500',     'dark': 'red/400'},
    'surface/status-critical-hover':   {'light': 'red/600', 'dark': 'red/300'},
    'surface/status-critical-pressed': {'light': 'red/700', 'dark': 'red/200'},
    'surface/status-critical-subtle': {'light': 'red/100',  'dark': '#381515'},
    'surface/status-critical-subtle-pressed': {'light': 'red/200', 'dark': '#4A1B1B'},
    'surface/status-caution':      {'light': 'amber/500',   'dark': 'amber/400'},
    'surface/status-caution-subtle': {'light': 'amber/100', 'dark': '#382B10'},
    'surface/status-good':         {'light': 'lime/500',    'dark': 'lime/400'},
    'surface/status-good-subtle':  {'light': 'lime/100',    'dark': '#25300F'},
    'surface/status-excellent':    {'light': 'green/600',   'dark': 'green/500'},
    'surface/status-excellent-subtle': {'light': 'green/100', 'dark': '#0F2C12'},
    # METRIC CATEGORY SURFACES (quick-status chips)
    'surface/metric-weight':       {'light': 'turquoise/100', 'dark': '#0F2E31'},
    'surface/metric-vaccine':      {'light': 'pink/100',      'dark': '#331030'},
    'surface/metric-activity':     {'light': 'blue/100',      'dark': '#152438'},
    'surface/metric-nutrition':    {'light': 'lime/100',      'dark': '#25300F'},
    'surface/metric-sleep':        {'light': 'violet/100',    'dark': '#241536'},
    'surface/metric-medication':   {'light': 'green/100',     'dark': '#0F2C12'},
    # TAG SURFACES (badges/chips for sex, category labels)
    'surface/tag-pink':            {'light': 'pink/500',      'dark': 'pink/500'},
    'surface/tag-violet':          {'light': 'violet/500',    'dark': 'violet/500'},
    'surface/tag-turquoise':       {'light': 'turquoise/700', 'dark': 'turquoise/700'},
    'surface/tag-pink-subtle':     {'light': 'pink/100',      'dark': '#331030'},
    'surface/tag-violet-subtle':   {'light': 'violet/100',    'dark': '#241536'},
    'surface/tag-turquoise-subtle':{'light': 'turquoise/100', 'dark': '#0F2E31'},
    # TEXT
    'text/default':      {'light': 'neutral/900', 'dark': '#F5F2EF'},
    'text/subtle':       {'light': 'neutral/600', 'dark': '#B3ACA5'},
    'text/muted':        {'light': 'neutral/400', 'dark': '#807A74'},
    'text/inverse':      {'light': '#F9F9F9',     'dark': 'neutral/900'},
    'text/brand':        {'light': 'brand/700',   'dark': 'brand/300'},
    'text/accent':       {'light': 'accent/700',  'dark': 'accent/300'},
    'text/link':         {'light': 'blue/500',    'dark': 'blue/300'},
    'text/disabled':     {'light': 'neutral/400', 'dark': '#5C5750'},
    'text/on-brand':     {'light': 'white',       'dark': 'chocolate/950'},
    'text/on-emphasis':  {'light': 'accent/50',   'dark': 'chocolate/950'},
    'text/on-status':    {'light': 'white',       'dark': 'chocolate/950'},
    'text/on-caution':   {'light': 'chocolate/950', 'dark': 'chocolate/950'},
    'text/on-good':      {'light': 'chocolate/950', 'dark': 'chocolate/950'},
    'text/tag-pink':     {'light': 'pink/700',      'dark': 'pink/300'},
    'text/tag-violet':   {'light': 'violet/700',    'dark': 'violet/300'},
    'text/tag-turquoise':{'light': 'turquoise/700', 'dark': 'turquoise/300'},
    'text/status-none':      {'light': 'blue/600',  'dark': 'blue/300'},
    'text/status-critical':  {'light': 'red/600',   'dark': 'red/300'},
    'text/status-caution':   {'light': 'amber/700', 'dark': 'amber/300'},
    'text/status-good':      {'light': 'lime/700',  'dark': 'lime/300'},
    'text/status-excellent': {'light': 'green/700', 'dark': 'green/300'},
    'text/metric-weight':     {'light': 'turquoise/700', 'dark': 'turquoise/300'},
    'text/metric-vaccine':    {'light': 'pink/700',      'dark': 'pink/300'},
    'text/metric-activity':   {'light': 'blue/700',      'dark': 'blue/300'},
    'text/metric-nutrition':  {'light': 'lime/700',      'dark': 'lime/300'},
    'text/metric-sleep':      {'light': 'violet/700',    'dark': 'violet/300'},
    'text/metric-medication': {'light': 'green/700',     'dark': 'green/300'},
    # ICON
    'icon/default':      {'light': 'neutral/900', 'dark': '#F5F2EF'},
    'icon/subtle':       {'light': 'neutral/600', 'dark': '#B3ACA5'},
    'icon/muted':        {'light': 'neutral/400', 'dark': '#807A74'},
    'icon/inverse':      {'light': '#F9F9F9',     'dark': 'neutral/900'},
    'icon/brand':        {'light': 'brand/600',   'dark': 'brand/300'},
    'icon/accent':       {'light': 'accent/600',  'dark': 'accent/300'},
    'icon/disabled':     {'light': 'neutral/400', 'dark': '#5C5750'},
    'icon/on-brand':     {'light': 'white',       'dark': 'chocolate/950'},
    'icon/on-emphasis':  {'light': 'accent/50',   'dark': 'chocolate/950'},
    'icon/status-none':      {'light': 'blue/600',  'dark': 'blue/300'},
    'icon/status-critical':  {'light': 'red/600',   'dark': 'red/300'},
    'icon/status-caution':   {'light': 'amber/700', 'dark': 'amber/300'},
    'icon/status-good':      {'light': 'lime/700',  'dark': 'lime/300'},
    'icon/status-excellent': {'light': 'green/700', 'dark': 'green/300'},
    # BORDER
    'border/default':    {'light': 'neutral/300', 'dark': '#3A3631'},
    'border/subtle':     {'light': 'neutral/200', 'dark': '#2E2B28'},
    'border/strong':     {'light': 'neutral/600', 'dark': '#807A74'},
    'border/brand':      {'light': 'brand/500',   'dark': 'brand/400'},
    'border/accent':     {'light': 'accent/500',  'dark': 'accent/400'},
    'border/selected':   {'light': 'brand/600',   'dark': 'brand/300'},
    'border/focus':      {'light': 'blue/500',    'dark': 'blue/300'},
    'border/disabled':   {'light': 'neutral/200', 'dark': '#2E2B28'},
    'border/status-critical': {'light': 'red/300',   'dark': 'red/700'},
    'border/status-caution':  {'light': 'amber/300', 'dark': 'amber/700'},
    'border/status-good':     {'light': 'lime/300',  'dark': 'lime/700'},
    'border/status-excellent':{'light': 'green/300', 'dark': 'green/700'},
    'border/status-none':     {'light': 'blue/300',  'dark': 'blue/700'},
}

# ---------- dimensions / radius / typography / numbers ----------
DIMENSION = {f'size/{k}': v for k, v in {
    '0': 0, '1': 2, '2': 4, '3': 8, '4': 12, '5': 16, '6': 20, '7': 24,
    '8': 28, '9': 32, '10': 40, '11': 48, '12': 56, '13': 64, '14': 80,
    '15': 96, '16': 128}.items()}

RADIUS = {'radius/xs': 6, 'radius/sm': 8, 'radius/md': 12, 'radius/lg': 16,
          'radius/xl': 20, 'radius/2xl': 24, 'radius/3xl': 32, 'radius/pill': 9999}

SEM_RADIUS = {
    'radius/control': 'radius/pill',      # KuKi buttons are pills
    'radius/control-compact': 'radius/2xl',
    'radius/badge': 'radius/xs',
    'radius/chip': 'radius/2xl',
    'radius/container': 'radius/3xl',     # cards
    'radius/container-nested': 'radius/2xl',
    'radius/dialog': 'radius/3xl',
    'radius/pill': 'radius/pill',
}

SEM_SPACE = {
    'space/inset-xs': 'size/2', 'space/inset-sm': 'size/3', 'space/inset-md': 'size/5',
    'space/inset-lg': 'size/7', 'space/inset-xl': 'size/9',
    'space/gap-2xs': 'size/1', 'space/gap-xs': 'size/2', 'space/gap-sm': 'size/3',
    'space/gap-md': 'size/5', 'space/gap-lg': 'size/7', 'space/gap-xl': 'size/10',
    'space/section-sm': 'size/7', 'space/section-md': 'size/10',
    'space/section-lg': 'size/12', 'space/section-xl': 'size/14',
}

# icon sizes — must be visibly distinct per step, or "scaling" reads as broken even
# when technically correct (12px vs 16px vs 20px is obvious; 16 vs 16 is not).
ICON_SIZE = {
    'icon-size/3xs': 'size/2',  # 4
    'icon-size/2xs': 'size/3',  # 8
    'icon-size/xs': 'size/4',   # 12
    'icon-size/sm': 'size/5',   # 16
    'icon-size/md': 'size/6',   # 20
    'icon-size/lg': 'size/7',   # 24
    'icon-size/xl': 'size/9',   # 32
}

FONT_FAMILY = 'Google Sans Flex'
FONT_STYLES = {'extralight': 'ExtraLight', 'light': 'Light', 'regular': 'Regular',
               'medium': 'Medium', 'semibold': 'SemiBold', 'bold': 'Bold'}
FONT_WEIGHTS = {'extralight': 200, 'light': 300, 'regular': 400,
                'medium': 500, 'semibold': 600, 'bold': 700}
FONT_SIZE = {'2xs': 10, 'xs': 12, 'sm': 14, 'md': 16, 'lg': 18, 'xl': 20,
             '2xl': 24, '3xl': 28, '4xl': 32, '5xl': 40, '6xl': 56}
LINE_HEIGHT = {'2xs': 14, 'xs': 16, 'sm': 20, 'md': 24, 'lg': 28, 'xl': 28,
               '2xl': 32, '3xl': 36, '4xl': 40, '5xl': 48, '6xl': 64}
TRACKING = {'tight': -0.2, 'normal': 0, 'wide': 0.8}

# text styles: name -> (style, size-key, tracking)
TEXT_STYLES = {
    'display/stat':  ('extralight', '6xl', 'tight'),
    'display/md':    ('semibold',   '5xl', 'tight'),
    'heading/h1':    ('semibold',   '4xl', 'tight'),
    'heading/h2':    ('semibold',   '3xl', 'tight'),
    'heading/h3':    ('semibold',   '2xl', 'normal'),
    'heading/h4':    ('semibold',   'xl',  'normal'),
    'title/lg':      ('semibold',   'lg',  'normal'),
    'title/md':      ('semibold',   'md',  'normal'),
    'body/lg':       ('regular',    'lg',  'normal'),
    'body/md':       ('regular',    'md',  'normal'),
    'body/sm':       ('regular',    'sm',  'normal'),
    'label/md':      ('medium',     'sm',  'normal'),
    'label/sm':      ('medium',     'xs',  'normal'),
    'caption':       ('regular',    'xs',  'normal'),
    'overline':      ('light',      '2xs', 'wide'),
}

NUMBER = {
    **{f'opacity/{k}': v for k, v in {'0': 0, '5': 0.05, '10': 0.1, '20': 0.2,
       '30': 0.3, '40': 0.4, '50': 0.5, '60': 0.6, '70': 0.7, '80': 0.8,
       '90': 0.9, '100': 1}.items()},
    'stroke/0': 0, 'stroke/1': 1, 'stroke/2': 2, 'stroke/3': 3, 'stroke/4': 4,
}
SEM_NUMBER = {'opacity/disabled': 'opacity/40', 'opacity/subtle': 'opacity/60',
              'opacity/overlay': 'opacity/50', 'stroke/default': 'stroke/1',
              'stroke/strong': 'stroke/2', 'stroke/focus': 'stroke/2'}

SHADOWS = {
    'shadow/sm': [{'y': 1, 'blur': 2, 'color': '#101010', 'alpha': 0.06}],
    'shadow/md': [{'y': 2, 'blur': 8, 'color': '#101010', 'alpha': 0.08}],
    'shadow/lg': [{'y': 8, 'blur': 24, 'color': '#101010', 'alpha': 0.12}],
    'shadow/xl': [{'y': 16, 'blur': 40, 'color': '#101010', 'alpha': 0.16}],
}

# ---------- resolvers / emit ----------
def resolve(ref):
    if ref.startswith('#') or ref.startswith('rgba'):
        return ref
    if ref in BASE:
        return BASE[ref]
    fam, step = ref.split('/')
    if fam in RAMPS:
        return RAMPS[fam][step]
    if fam in EXTENDED:
        return EXTENDED[fam][step]
    raise KeyError(ref)

def css_name(name):
    return '--kuki-' + name.replace('/', '-')

def emit():
    out_dir = os.path.dirname(os.path.abspath(__file__))
    # tokens.json
    tokens = {
        'primitives': {'color': {**{f'{f}/{s}': v for f, r in {**RAMPS, **EXTENDED}.items() for s, v in r.items()},
                                 **BASE},
                       'dimension': DIMENSION, 'radius': RADIUS,
                       'typography': {'family': FONT_FAMILY, 'styles': FONT_STYLES,
                                      'weights': FONT_WEIGHTS, 'size': FONT_SIZE,
                                      'lineHeight': LINE_HEIGHT, 'tracking': TRACKING},
                       'number': NUMBER, 'shadow': SHADOWS, 'gradients': GRADIENTS},
        'semantic': {'color': SEMANTIC_COLOR, 'radius': SEM_RADIUS, 'space': SEM_SPACE,
                     'iconSize': ICON_SIZE, 'number': SEM_NUMBER, 'textStyles': TEXT_STYLES},
    }
    with open(os.path.join(out_dir, 'tokens.json'), 'w') as f:
        json.dump(tokens, f, indent=2)

    # figma-vars.json (flat, with resolved values for both modes)
    fig = {
        'primitives_color': {f'{fam}/{s}': v for fam, r in {**RAMPS, **EXTENDED}.items() for s, v in r.items()},
        'base': BASE,
        'semantic_color': {n: {'light': resolve(m['light']),
                               'dark': resolve(m['dark']),
                               'lightRef': m['light'] if '/' in m['light'] or m['light'] in BASE else None,
                               'darkRef': m['dark'] if '/' in m['dark'] or m['dark'] in BASE else None}
                           for n, m in SEMANTIC_COLOR.items()},
        'dimension': DIMENSION, 'radius': RADIUS, 'sem_radius': SEM_RADIUS,
        'sem_space': SEM_SPACE, 'sem_icon_size': ICON_SIZE, 'number': NUMBER, 'sem_number': SEM_NUMBER,
        'font': {'family': FONT_FAMILY, 'styles': FONT_STYLES, 'weights': FONT_WEIGHTS,
                 'size': FONT_SIZE, 'lineHeight': LINE_HEIGHT, 'tracking': TRACKING},
        'text_styles': TEXT_STYLES, 'shadows': SHADOWS, 'gradients': GRADIENTS,
    }
    with open(os.path.join(out_dir, 'figma-vars.json'), 'w') as f:
        json.dump(fig, f, indent=2)

    # tokens.css
    lines = ['/* KuKi Design System — generated by generate_tokens.py. Do not hand-edit. */', ':root {']
    for fam, ramp in {**RAMPS, **EXTENDED}.items():
        for s, v in ramp.items():
            lines.append(f'  {css_name(f"color-{fam}-{s}")}: {v};')
    for k, v in BASE.items():
        lines.append(f'  {css_name(f"color-{k}")}: {v};')
    for k, v in DIMENSION.items():
        lines.append(f'  {css_name(k)}: {v}px;')
    for k, v in RADIUS.items():
        lines.append(f'  {css_name(k)}: {v}px;')
    for k, ref in SEM_RADIUS.items():
        lines.append(f'  {css_name("sem-" + k)}: var({css_name(ref)});')
    for k, ref in SEM_SPACE.items():
        lines.append(f'  {css_name(k)}: var({css_name(ref)});')
    for k, ref in ICON_SIZE.items():
        lines.append(f'  {css_name(k)}: var({css_name(ref)});')
    for k, v in NUMBER.items():
        lines.append(f'  {css_name(k)}: {v};')
    for k, ref in SEM_NUMBER.items():
        lines.append(f'  {css_name("sem-" + k)}: var({css_name(ref)});')
    lines.append(f'  {css_name("font-family")}: "{FONT_FAMILY}", system-ui, sans-serif;')
    for k, v in FONT_WEIGHTS.items():
        lines.append(f'  {css_name(f"font-weight-{k}")}: {v};')
    for k, v in FONT_SIZE.items():
        lines.append(f'  {css_name(f"font-size-{k}")}: {v}px;')
    for k, v in LINE_HEIGHT.items():
        lines.append(f'  {css_name(f"line-height-{k}")}: {v}px;')
    for name, shadow in SHADOWS.items():
        parts = [f'0 {s["y"]}px {s["blur"]}px rgba(16,16,16,{s["alpha"]})' for s in shadow]
        lines.append(f'  {css_name(name)}: {", ".join(parts)};')
    for name, stops in GRADIENTS.items():
        # CSS's `circle` keyword computes an equal-radius circle regardless of the
        # box's own aspect ratio — unlike Figma, which needs a compensating matrix.
        lines.append(f'  {css_name("gradient-" + name)}: radial-gradient(circle at 50% 50%, {stops[0]} 0%, {stops[1]} 40%, {stops[2]} 60%, {stops[-1]} 100%);')
    lines.append('}')

    def mode_block(selector, mode):
        b = [f'{selector} {{']
        for n, m in SEMANTIC_COLOR.items():
            b.append(f'  {css_name("sem-" + n)}: {resolve(m[mode])};')
        b.append('}')
        return b

    lines += mode_block(':root, [data-theme="light"]', 'light')
    lines += ['', '@media (prefers-color-scheme: dark) {'] + \
             ['  ' + l for l in mode_block(':root:not([data-theme="light"])', 'dark')] + ['}']
    lines += mode_block('[data-theme="dark"]', 'dark')

    os.makedirs(os.path.join(out_dir, 'css'), exist_ok=True)
    with open(os.path.join(out_dir, 'css', 'tokens.css'), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(f'wrote tokens.json ({len(json.dumps(tokens))} bytes), figma-vars.json, css/tokens.css')

if __name__ == '__main__':
    print('WCAG contrast checks:')
    failed = run_checks()
    emit()
    if failed:
        print('\nFAILED CHECKS:')
        for label, r in failed:
            print(f'  {label}: {r:.2f}')
        raise SystemExit(1)
    print('all contrast checks passed')
